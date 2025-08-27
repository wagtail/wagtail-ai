import { Controller } from '@hotwired/stimulus';
import { APIRequestError, fetchResponse, getAIConfiguration } from '../api';
import './main.css';

export enum DefaultPrompt {
  CORRECTION = 1,
  COMPLETION = 2,
  DESCRIPTION = 3,
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

class PromptController extends Controller<HTMLButtonElement> {
  declare input: HTMLInputElement | HTMLTextAreaElement;

  connect() {
    const input = this.element
      .closest('[data-field-input]')
      ?.querySelector<
        HTMLInputElement | HTMLTextAreaElement
      >('input, textarea');
    if (!input) {
      throw new Error('Could not find input or textarea element.');
    }
    this.input = input;
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
    const {
      promptId,
      method = PromptMethod.APPEND,
      useContent = false,
    } = {
      ...event?.detail,
      ...event?.params,
    };
    const data = new FormData();
    let text = this.input.value;
    if (useContent) {
      const { innerText = '' } = (await this.getPreviewContent()) || {};
      text = innerText;
    }
    data.append('text', text);
    data.append('prompt', promptId!);
    this.input.readOnly = true;

    let result = '';
    try {
      result = await fetchResponse('TEXT_COMPLETION', data);
    } catch (error) {
      console.error(error);
      if (error instanceof APIRequestError) {
        alert(error.message);
      } else {
        alert('An unknown error occurred. Please try again.');
      }
    }

    this.input.readOnly = false;
    if (!result) return;

    if (method === PromptMethod.APPEND) {
      this.input.value += result;
    } else if (method === PromptMethod.REPLACE) {
      this.input.value = result;
    }
    this.input.dispatchEvent(new Event('input', { bubbles: true }));
  }
}

class FieldPanelController extends Controller<HTMLTemplateElement> {
  static targets = ['dropdown'];
  declare dropdownTarget: HTMLTemplateElement;
  declare input: HTMLElement;

  connect() {
    this.input = this.element.querySelector('[data-field-input]')!;
    // If the field has a comment button, insert the dropdown before it to ensure
    // the tab order is correct. Otherwise just append it to the end of the input.
    const commentButton = this.element.querySelector('[data-comment-add]');
    if (commentButton) {
      this.input.insertBefore(this.template, commentButton);
    } else {
      this.input.appendChild(this.template);
    }

    this.dropdownTarget.remove();
  }

  get template() {
    const root = this.dropdownTarget.content.firstElementChild!.cloneNode(
      true,
    ) as HTMLElement;
    const content = root.querySelector('[data-w-dropdown-target="content"]')!;
    getAIConfiguration().aiPrompts.forEach((prompt) => {
      const useContent = prompt.default_prompt_id === DefaultPrompt.DESCRIPTION;
      content.insertAdjacentHTML(
        'beforeend',
        /* html */ `
        <button
          type="button"
          class="wai-dropdown__item"
          data-action="click->wai-prompt#prompt"
          data-wai-prompt-prompt-id-param="${prompt.uuid}"
          data-wai-prompt-method-param="${prompt.method}"
          data-wai-prompt-use-content-param="${useContent}"
        >
          <div>${prompt.label}</div>
          <div class="wai-dropdown__description">${prompt.description}</div>
        </button>
      `,
      );
    });
    root.setAttribute(
      'data-controller',
      `wai-prompt ${root.getAttribute('data-controller') || ''}`.trim(),
    );
    return root;
  }
}

window.wagtail.app.register('wai-prompt', PromptController);
window.wagtail.app.register('wai-field-panel', FieldPanelController);
