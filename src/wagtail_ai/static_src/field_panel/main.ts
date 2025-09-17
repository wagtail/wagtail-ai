import { Controller } from '@hotwired/stimulus';
import { fetchResponse } from '../api';
import './main.css';
import { DefaultPrompt, PromptMethod } from '../constants';
import { Prompt } from '../custom';

interface PromptOptions {
  promptId: string;
}

interface PreviewContent {
  lang: string;
  innerText: string;
  innerHTML: string;
}

enum FieldPanelState {
  IDLE = 'idle',
  LOADING = 'loading',
  ERROR = 'error',
  SUGGESTING = 'suggesting',
}

/**
 * Stub for Wagtail's DropdownController.
 * https://docs.wagtail.org/en/stable/reference/ui/client/classes/controllers_DropdownController.DropdownController.html
 */
interface DropdownController extends Controller {
  tippy: any;
  toggleTarget: HTMLElement;
  contentTarget: HTMLElement;
}

type ContextHandler = (
  this: FieldPanelController,
) => Promise<string | null | undefined>;

export class ContextProvider {
  static handlers: Record<string, ContextHandler> = {};
  static register(name: string, handler: ContextHandler) {
    this.handlers[name] = handler;
  }

  static async get(controller: FieldPanelController) {
    const context: Record<string, string> = {};
    await Promise.allSettled(
      Object.entries(ContextProvider.handlers).map(async ([key, handler]) => {
        if (!controller.activePrompt?.prompt.includes(`{${key}}`)) return;
        const result = await handler.call(controller);
        if (![null, undefined].includes(result)) context[key] = result;
      }),
    );
    return context;
  }
}

type InputType = HTMLInputElement | HTMLTextAreaElement | HTMLDivElement;

class FieldPanelController extends Controller<HTMLElement> {
  static targets = ['dropdown', 'prompt', 'suggestion'];
  static values = {
    activePromptId: { type: String, default: '' },
    dropdownTemplate: {
      type: String,
      default: '#wai-field-panel-dropdown-template',
    },
    imageInput: { type: String, default: '' },
    mainInput: { type: String, default: '' },
    prompts: { type: Array, default: [] },
    state: { type: String, default: FieldPanelState.IDLE },
    suggestion: { type: String, default: '' },
  };
  declare hasDropdownTarget: boolean;
  declare dropdownTarget: HTMLDivElement;
  declare promptTargets: HTMLButtonElement[];
  declare hasSuggestionTarget: boolean;
  declare suggestionTarget: HTMLDivElement;
  declare activePromptIdValue: string;
  declare dropdownTemplateValue: string;
  declare imageInputValue: string;
  declare mainInputValue: string;
  declare promptsValue: DefaultPrompt[];
  declare stateValue: FieldPanelState;
  declare suggestionValue: string;
  declare filteredPrompts: Prompt[];
  declare fieldInput: HTMLElement;
  declare input: InputType;
  activePrompt: Prompt | null = null;
  abortController: AbortController | null = null;
  imageInput: HTMLInputElement | null = null;
  dropdownController: DropdownController | null = null;

  static defaultHandlers = {
    async content_html(this: FieldPanelController) {
      return (await this.getPreviewContent())?.innerHTML;
    },
    async content_text(this: FieldPanelController) {
      return (await this.getPreviewContent())?.innerText;
    },
    async form_context_before(this: FieldPanelController) {
      return this.formContext.before;
    },
    async form_context_after(this: FieldPanelController) {
      return this.formContext.after;
    },
    async image_id(this: FieldPanelController) {
      // Allow the image input to be of type="file"
      if (this.imageInput?.files?.[0]) {
        return new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result as string);
          reader.onerror = reject;
          reader.readAsDataURL(this.imageInput!.files![0]);
        });
      }

      return (
        this.imageInput?.value ||
        // Allow the image ID to be provided directly via a data attribute
        this.element.getAttribute(`data-${this.identifier}-image-id`)
      );
    },
    async input(this: FieldPanelController) {
      return this.inputValue;
    },
    async max_length(this: FieldPanelController) {
      return this.input.getAttribute('maxlength');
    },
  };

  static {
    Object.entries(this.defaultHandlers).forEach(([name, handler]) => {
      ContextProvider.register(name, handler);
    });
  }

  /**
   * Convert an array of input elements into a single string,
   * concatenating their values or inner text.
   * @param inputs an array of input, textarea, or div elements
   * @returns {string} The concatenated text from the inputs
   */
  static inputsToText = (
    inputs: Array<HTMLInputElement | HTMLTextAreaElement | HTMLDivElement>,
  ): string =>
    inputs
      .map((input) => ('value' in input ? input.value : input.innerText))
      .filter((text) => !!text.trim())
      .join('\n\n');

  connect() {
    // If connecting to an input directly, don't render the dropdown until we
    // reconnect the controller to the field wrapper element.
    // If the dropdown target already exists, it's likely already rendered and
    // this controller was reconnected after a block was reordered.
    if (this.#connectedDirectlyToInput || this.hasDropdownTarget) return;

    this.getPreviewContent = this.getPreviewContent.bind(this);

    // If the field has a comment button, insert the dropdown before it to ensure
    // the tab order is correct. Otherwise just append it to the end of the input.
    const commentButton = this.fieldInput.querySelector('[data-comment-add]');
    if (commentButton) {
      this.fieldInput.insertBefore(this.template, commentButton);
    } else {
      this.fieldInput.appendChild(this.template);
    }
  }

  /**
   * Whether this controller is connected directly to an input element,
   * rather than a wrapper element such as data-field-wrapper. This may
   * happen for form fields that are not rendered using Wagtail's Panels API,
   * so the controller is attached using attributes on the input widget instead.
   */
  get #connectedDirectlyToInput() {
    return (
      this.element instanceof HTMLInputElement ||
      this.element instanceof HTMLTextAreaElement ||
      this.element.isContentEditable
    );
  }

  get template() {
    const template = document.querySelector<HTMLTemplateElement>(
      this.dropdownTemplateValue,
    )?.content?.firstElementChild;
    if (!template) {
      throw new Error('Could not find dropdown template element.');
    }

    const root = template!.cloneNode(true) as HTMLElement;

    // Insert before other contents of the dropdown
    // i.e. the intermediary and suggestion containers.
    const before = root.querySelector(
      '[data-w-dropdown-target="content"]',
    )!.firstElementChild!;

    this.filteredPrompts.forEach((prompt) => {
      before.insertAdjacentHTML(
        'beforebegin',
        this.getDropdownItemTemplate(prompt),
      );
    });
    return root;
  }

  getDropdownItemTemplate(prompt: Prompt) {
    return /* html */ `
      <button
        type="button"
        class="wai-dropdown__item"
        data-action="click->wai-field-panel#prompt"
        data-wai-field-panel-target="prompt"
        data-wai-field-panel-prompt-id-param="${prompt.uuid}"
      >
        <div>${prompt.label}</div>
        <div class="wai-dropdown__description">${prompt.description}</div>
      </button>
    `;
  }

  dropdownTargetConnected() {
    // Use timeout to wait until the dropdown controller is connected to the
    // element. Ideally we should listen for an event from the dropdown
    // controller when it's ready, but it currently doesn't emit any events on
    // connection.
    // Alternatively, we could use a Stimulus outlet instead of a target, but
    // outlets aren't scoped, so we need a unique identifier as the selector,
    // which we do not have.
    setTimeout(() => {
      this.dropdownController =
        window.wagtail.app.getControllerForElementAndIdentifier(
          this.dropdownTarget,
          'w-dropdown',
        ) as DropdownController;
      this.setDropdownTheme();
    });
  }

  setDropdownTheme() {
    const { tippy } = this.dropdownController!;
    // Set a fixed with via CSS and use a custom theme, so this can later be
    // incorporated into Wagtail core as a new DropdownController theme.
    tippy.setProps({
      arrow: false,
      maxWidth: 'none',
      theme: 'assistant',
    });
  }

  imageInputValueChanged() {
    if (this.#connectedDirectlyToInput || !this.imageInputValue) return;
    const input =
      // Look within the scope first for more specific elements
      // (e.g. inside a StructBlock)
      this.element.querySelector<HTMLInputElement>(this.imageInputValue) ||
      // Then fall back to the whole form
      // (e.g. when the controller is connected to a form field that was rendered
      // without the Panels API).
      this.form!.querySelector<HTMLInputElement>(this.imageInputValue);
    this.imageInput = input;
  }

  mainInputValueChanged() {
    if (this.#connectedDirectlyToInput) {
      // If the controller is attached directly to the input element, reconnect
      // it on the data-field-wrapper element instead, because we need to add
      // and control elements around the input itself.
      const fieldWrapper = this.element.closest('[data-field-wrapper]')!;
      Array.from(this.element.attributes).forEach((attr) => {
        if (attr.name === 'data-controller') {
          // Move this controller to the field wrapper element,
          // alongside any other controllers already attached there.
          const fieldWrapperControllers = new Set(
            fieldWrapper.getAttribute('data-controller')?.split(' ') || [],
          );
          fieldWrapperControllers.add(this.identifier);
          fieldWrapper.setAttribute(
            'data-controller',
            Array.from(fieldWrapperControllers).join(' '),
          );

          // Disconnect this controller from the input element,
          // keeping any other controllers.
          this.element.setAttribute(
            'data-controller',
            attr.value
              .split(' ')
              .filter((c) => c !== this.identifier)
              .join(' '),
          );
        }

        // Copy over any data attributes for this controller from the input to
        // the field wrapper. The cleanup of attributes on the input will be
        // done in disconnect() below, as there might be other attributes added
        // to the element that do not yet exist when this method runs.
        if (attr.name.startsWith(`data-${this.identifier}-`)) {
          fieldWrapper.setAttribute(attr.name, attr.value);
        }

        // We don't copy data-action, as we don't currently expect any methods
        // in this controller to be used as an action on the input.
      });
      return;
    } else if (this.mainInputValue) {
      // If a selector is provided, use that to find the input.
      const input = this.element.querySelector<InputType>(this.mainInputValue);
      if (!input) {
        throw new Error(
          `Could not find input element matching selector "${this.mainInputValue}".`,
        );
      }

      this.input = input;
      this.fieldInput = this.input.closest('[data-field-input]')!;
    } else {
      // This controller is likely attached to a panel-like wrapper,
      // find the field input container and then the input inside it.
      this.fieldInput = this.element.querySelector('[data-field-input]')!;
      const input = this.fieldInput.querySelector<InputType>('input, textarea');
      if (!input) {
        throw new Error('Could not find input or textarea element.');
      }
      this.input = input;
    }
  }

  /**
   * All text inputs in the form.
   */
  get textInputs(): InputType[] {
    return Array.from(
      this.form!.querySelectorAll<InputType>(
        'input[type="text"], textarea, [role="textbox"]',
      ),
    ).filter((input) => input !== this.input);
  }

  /**
   * Text inputs in the form, grouped by their position
   * relative to the main input (before/after).
   */
  get textInputsContext() {
    return Object.groupBy(this.textInputs, (element) =>
      this.input.compareDocumentPosition(element) &
      Node.DOCUMENT_POSITION_PRECEDING
        ? 'before'
        : 'after',
    ) as { before: InputType[]; after: InputType[] };
  }

  /**
   * Get the form context as plain text, grouped by inputs
   * before and after the main input.
   */
  get formContext() {
    const { inputsToText } = FieldPanelController;
    const { before, after } = this.textInputsContext;
    return {
      before: inputsToText(before),
      after: inputsToText(after),
    };
  }

  get form() {
    if (!this.input) this.mainInputValueChanged();
    return (
      ('form' in this.input ? this.input.form : null) ??
      this.input.closest('form')
    );
  }

  get inputValue() {
    return 'value' in this.input ? this.input.value : this.input.innerText;
  }

  set inputValue(value: string) {
    if ('value' in this.input) {
      this.input.value = value;
    } else {
      this.input.innerText = value;
    }
  }

  promptsValueChanged() {
    if (!this.promptsValue.length) {
      this.filteredPrompts = window.wagtailAI.config.aiPrompts;
      return;
    }
    this.filteredPrompts = window.wagtailAI.config.aiPrompts.filter(
      ({ default_prompt_id }) =>
        default_prompt_id && this.promptsValue.includes(default_prompt_id),
    );
  }

  activePromptIdValueChanged() {
    this.activePrompt =
      window.wagtailAI.config.aiPrompts.find(
        (p) => p.uuid === this.activePromptIdValue,
      ) ?? null;
  }

  async getPreviewContent(): Promise<PreviewContent | null> {
    const preview: any = window.wagtail.app.queryController('w-preview');
    if (!preview) return null;
    if (!preview.ready) {
      // Preview panel likely has not been opened, force it to load the preview.
      await preview.checkAndUpdatePreview();
      await new Promise((resolve) => {
        document.addEventListener('w-preview:loaded', resolve, { once: true });
      });
    }
    return preview.extractContent();
  }

  async prompt(
    event?: CustomEvent<PromptOptions> & { params?: PromptOptions },
  ) {
    const { promptId = this.activePromptIdValue } = {
      ...event?.detail,
      ...event?.params,
    };
    this.stateValue = FieldPanelState.LOADING;
    this.activePromptIdValue = promptId;
    // The setter above only sets the data attribute, and Stimulus runs the
    // callback asynchronously when the MutationObserver notices the change.
    // Call the callback manually to ensure `this.activePrompt` is set.
    this.activePromptIdValueChanged();

    const data = new FormData();
    data.append('context', JSON.stringify(await ContextProvider.get(this)));
    data.append('prompt', promptId!);

    let result = '';
    try {
      this.abortController = new AbortController();
      result = await fetchResponse(
        'TEXT_COMPLETION',
        data,
        this.abortController!.signal,
      );
    } catch (error) {
      if (this.abortController?.signal.aborted) {
        this.stateValue = FieldPanelState.IDLE;
        this.abortController = null;
        return;
      }
      this.stateValue = FieldPanelState.ERROR;
      console.error(error);
    }
    if (!result) return;

    this.stateValue = FieldPanelState.SUGGESTING;
    this.suggestionValue = result;
  }

  stateValueChanged() {
    const toggleTarget = this.dropdownController?.toggleTarget;
    const icon = toggleTarget?.querySelector('svg use');
    icon?.setAttribute(
      'href',
      this.stateValue === FieldPanelState.LOADING
        ? '#icon-wand-animated'
        : '#icon-wand',
    );

    this.togglePrompts();
    if (this.stateValue === FieldPanelState.IDLE) this.reset();
  }

  suggestionValueChanged() {
    if (!this.hasSuggestionTarget) return;
    this.suggestionTarget.innerText = this.suggestionValue;
  }

  togglePrompts() {
    switch (this.stateValue) {
      case FieldPanelState.LOADING:
      case FieldPanelState.ERROR:
        this.promptTargets.forEach((button) => (button.hidden = true));
        break;
      case FieldPanelState.SUGGESTING:
        this.promptTargets.forEach(
          (button) =>
            (button.hidden =
              button.getAttribute('data-wai-field-panel-prompt-id-param') !==
              this.activePromptIdValue),
        );
        break;
      case FieldPanelState.IDLE:
      default:
        this.promptTargets.forEach((button) => (button.hidden = false));
        break;
    }
  }

  useSuggestion() {
    if (this.activePrompt?.method === PromptMethod.APPEND) {
      this.inputValue += this.suggestionValue;
    } else {
      this.inputValue = this.suggestionValue;
    }
    // Trigger autosize if available
    this.input.dispatchEvent(new Event('input', { bubbles: true }));
    // Trigger change event so others e.g. TitleFieldPanel can pick up the change
    this.input.dispatchEvent(new Event('change', { bubbles: true }));
  }

  reset() {
    this.stateValue = FieldPanelState.IDLE;
    this.abortController?.abort('Cancelled by user');
    this.suggestionValue = '';
    this.activePromptIdValue = '';
  }

  disconnect(): void {
    if (!this.#connectedDirectlyToInput) return;
    // Clean up any data attributes for this controller added to the input,
    // as the controller is moved to the field wrapper element.
    Array.from(this.element.attributes).forEach((attr) => {
      if (
        (attr.name === 'data-controller' && !attr.value) ||
        attr.name.startsWith(`data-${this.identifier}-`)
      )
        this.element.removeAttribute(attr.name);
    });
  }
}

window.wagtail.app.register('wai-field-panel', FieldPanelController);
window.wagtailAI.ContextProvider = ContextProvider;
