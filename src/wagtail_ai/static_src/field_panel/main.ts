import { Controller } from '@hotwired/stimulus';
import { fetchResponse } from '../api';
import './main.css';
import { Prompt } from '../custom';

export enum DefaultPrompt {
  CORRECTION = 1,
  COMPLETION = 2,
  DESCRIPTION = 3,
  TITLE = 4,
}

export enum PromptMethod {
  APPEND = 'append',
  REPLACE = 'replace',
}

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

class FieldPanelController extends Controller<HTMLTemplateElement> {
  static targets = ['dropdown', 'prompt', 'suggestion'];
  static values = {
    activePromptId: { type: String, default: '' },
    dropdownTemplate: {
      type: String,
      default: '#wai-field-panel-dropdown-template',
    },
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
  declare promptsValue: DefaultPrompt[];
  declare stateValue: FieldPanelState;
  declare suggestionValue: string;
  declare filteredPrompts: Prompt[];
  declare fieldInput: HTMLElement;
  declare input: HTMLInputElement | HTMLTextAreaElement;
  activePrompt: Prompt | null = null;
  abortController: AbortController | null = null;
  dropdownController: DropdownController | null = null;

  connect() {
    // If the dropdown target already exists, it's likely already rendered and
    // this controller was reconnected after a block was reordered.
    if (this.hasDropdownTarget) return;

    this.fieldInput = this.element.querySelector('[data-field-input]')!;
    // If the field has a comment button, insert the dropdown before it to ensure
    // the tab order is correct. Otherwise just append it to the end of the input.
    const commentButton = this.element.querySelector('[data-comment-add]');
    if (commentButton) {
      this.fieldInput.insertBefore(this.template, commentButton);
    } else {
      this.fieldInput.appendChild(this.template);
    }

    const input = this.fieldInput.querySelector<
      HTMLInputElement | HTMLTextAreaElement
    >('input, textarea');
    if (!input) {
      throw new Error('Could not find input or textarea element.');
    }
    this.input = input;
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

    const useContent = [
      DefaultPrompt.DESCRIPTION,
      DefaultPrompt.TITLE,
    ].includes(this.activePrompt!.default_prompt_id!);
    const data = new FormData();
    let text = this.input.value;
    if (useContent) {
      const { innerText = '' } = (await this.getPreviewContent()) || {};
      text = innerText;
    }
    data.append('text', text);
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
      this.input.value += this.suggestionValue;
    } else {
      this.input.value = this.suggestionValue;
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
}

window.wagtail.app.register('wai-field-panel', FieldPanelController);
