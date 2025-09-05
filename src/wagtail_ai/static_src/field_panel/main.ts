import { Controller } from '@hotwired/stimulus';
import { APIRequestError, fetchResponse } from '../api';
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
  method: PromptMethod;
  useContent?: boolean;
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

class FieldPanelController extends Controller<HTMLTemplateElement> {
  static classes = ['idle', 'loading', 'error', 'suggesting'];
  static targets = ['dropdown', 'prompt', 'suggestion'];
  static values = {
    activePromptId: { type: String, default: '' },
    prompts: { type: Array, default: [] },
    state: { type: String, default: FieldPanelState.IDLE },
    suggestion: { type: String, default: '' },
  };
  declare idleClass: string;
  declare loadingClass: string;
  declare errorClass: string;
  declare suggestingClass: string;
  declare dropdownTarget: HTMLTemplateElement;
  declare promptTargets: HTMLButtonElement[];
  declare hasSuggestionTarget: boolean;
  declare suggestionTarget: HTMLDivElement;
  declare activePromptIdValue: string;
  declare promptsValue: DefaultPrompt[];
  declare stateValue: FieldPanelState;
  declare suggestionValue: string;
  declare filteredPrompts: Prompt[];
  declare fieldInput: HTMLElement;
  declare input: HTMLInputElement | HTMLTextAreaElement;
  abortController: AbortController | null = null;

  connect() {
    this.fieldInput = this.element.querySelector('[data-field-input]')!;
    // If the field has a comment button, insert the dropdown before it to ensure
    // the tab order is correct. Otherwise just append it to the end of the input.
    const commentButton = this.element.querySelector('[data-comment-add]');
    if (commentButton) {
      this.fieldInput.insertBefore(this.template, commentButton);
    } else {
      this.fieldInput.appendChild(this.template);
    }

    this.dropdownTarget.remove();

    const input = this.fieldInput.querySelector<
      HTMLInputElement | HTMLTextAreaElement
    >('input, textarea');
    if (!input) {
      throw new Error('Could not find input or textarea element.');
    }
    this.input = input;
  }

  get template() {
    const root = this.dropdownTarget.content.firstElementChild!.cloneNode(
      true,
    ) as HTMLElement;
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
    const useContent = [
      DefaultPrompt.DESCRIPTION,
      DefaultPrompt.TITLE,
    ].includes(prompt.default_prompt_id!);
    return /* html */ `
      <button
        type="button"
        class="wai-dropdown__item"
        data-action="click->wai-field-panel#prompt"
        data-wai-field-panel-target="prompt"
        data-wai-field-panel-prompt-id-param="${prompt.uuid}"
        data-wai-field-panel-method-param="${prompt.method}"
        data-wai-field-panel-use-content-param="${useContent}"
      >
        <div>${prompt.label}</div>
        <div class="wai-dropdown__description">${prompt.description}</div>
      </button>
    `;
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
    const { promptId = this.activePromptIdValue, useContent = false } = {
      ...event?.detail,
      ...event?.params,
    };
    this.stateValue = FieldPanelState.LOADING;
    this.activePromptIdValue = promptId!;

    const icon = this.element.querySelector('svg use');
    const data = new FormData();
    let text = this.input.value;
    if (useContent) {
      const { innerText = '' } = (await this.getPreviewContent()) || {};
      text = innerText;
    }
    data.append('text', text);
    data.append('prompt', promptId!);
    icon?.setAttribute('href', '#icon-wand-animated');

    let result = '';
    try {
      this.abortController = new AbortController();
      result = await fetchResponse(
        'TEXT_COMPLETION',
        data,
        this.abortController.signal,
      );
    } catch (error) {
      if (this.abortController?.signal.aborted) {
        this.stateValue = FieldPanelState.IDLE;
        this.abortController = null;
        return;
      }
      this.stateValue = FieldPanelState.ERROR;
      console.error(error);
      if (error instanceof APIRequestError) {
        alert(error.message);
      } else {
        alert('An unknown error occurred. Please try again.');
      }
    }

    icon?.setAttribute('href', '#icon-wand');
    if (!result) return;

    this.stateValue = FieldPanelState.SUGGESTING;
    this.suggestionValue = result;
  }

  stateValueChanged() {
    const classes = {
      [FieldPanelState.IDLE]: this.idleClass,
      [FieldPanelState.LOADING]: this.loadingClass,
      [FieldPanelState.ERROR]: this.errorClass,
      [FieldPanelState.SUGGESTING]: this.suggestingClass,
    };
    Object.entries(classes).forEach(([state, className]) => {
      this.element.classList.toggle(className, state === this.stateValue);
    });

    switch (this.stateValue) {
      case FieldPanelState.IDLE:
        this.reset();
        break;
      case FieldPanelState.LOADING:
        this.hideAllPrompts();
        break;
      case FieldPanelState.ERROR:
        this.hideAllPrompts();
        break;
      case FieldPanelState.SUGGESTING:
        this.hideInactivePrompts();
        break;
    }
  }

  suggestionValueChanged() {
    if (!this.hasSuggestionTarget) return;
    this.suggestionTarget.innerText = this.suggestionValue;
  }

  hideAllPrompts() {
    this.promptTargets.forEach((button) => (button.hidden = true));
  }

  hideInactivePrompts() {
    this.promptTargets.forEach(
      (button) =>
        (button.hidden =
          button.getAttribute('data-wai-field-panel-prompt-id-param') !==
          this.activePromptIdValue),
    );
  }

  useSuggestion() {
    this.input.value = this.suggestionValue;
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
    this.promptTargets.forEach((button) => (button.hidden = false));
  }
}

window.wagtail.app.register('wai-field-panel', FieldPanelController);
