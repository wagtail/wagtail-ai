import { Controller } from '@hotwired/stimulus';
import './main.css';
import { getPreviewContent } from '../preview';

enum ChooserSuggestionState {
  INITIAL = 'initial',
  LOADING = 'loading',
  ERROR = 'error',
  SUGGESTED = 'suggested',
  NO_MORE = 'no_more',
}

class ChooserPanelController extends Controller<HTMLElement> {
  static targets = ['suggestButton'];
  static values = {
    relationName: String,
    url: {
      default: window.wagtailAI.config.urls.SUGGESTED_CONTENT,
      type: String,
    },
    state: {
      default: ChooserSuggestionState.INITIAL,
      type: String,
    },
    seenPks: {
      default: [],
      type: Array,
    },
    vectorIndex: String,
    instancePk: String,
    limit: Number,
    chunkSize: Number,
  };
  declare relationNameValue: string;
  declare urlValue: string;
  declare instancePkValue: string;
  declare vectorIndexValue: string;
  declare limitValue: number;
  declare seenPksValue: [string?];
  declare stateValue: ChooserSuggestionState;
  declare chunkSizeValue: number;
  declare hasChunkSizeValue: boolean;
  declare suggestButtonTarget: HTMLButtonElement;
  abortController: AbortController | null = null;
  #panelComponent: any | null = null;

  connect() {
    this.stateValue = ChooserSuggestionState.INITIAL;
  }

  get panelComponent() {
    if (!this.#panelComponent) {
      this.#panelComponent = window.wagtail.editHandler.getPanelByName(
        this.relationNameValue,
      )!;
    }
    return this.#panelComponent;
  }

  addItem(item: any) {
    const panel = this.panelComponent;
    panel.addForm();
    const formIndex = panel.formCount - 1;
    const formPrefix = `${panel.opts.formsetPrefix}-${formIndex}`;
    const chooserFieldId = `${formPrefix}-${panel.opts.chooserFieldName}`;
    const chooserPanel: HTMLElement | null = document.querySelector(
      `[data-inline-panel-child]:has(#${chooserFieldId})`,
    );
    if (chooserPanel) {
      chooserPanel.setAttribute(`data-${this.identifier}-suggested`, 'true');
      const chooserWidget = panel.chooserWidgetFactory.getById(chooserFieldId);
      chooserWidget.setState({
        id: item.id,
        adminTitle: item.title,
        editUrl: item.editUrl,
      });
    }
  }

  async getSuggestions() {
    const previewContent = await getPreviewContent();
    if (!previewContent) {
      throw new Error('Unable to get page content for analysis.');
    }

    let limit = this.limitValue;
    const maxForms = this.panelComponent.opts.maxForms;
    if (maxForms) {
      limit = Math.min(
        maxForms - this.panelComponent.getChildCount(),
        this.limitValue,
      );
    }

    const { innerText } = previewContent;

    try {
      const response = await fetch(this.urlValue, {
        method: 'POST',
        headers: {
          [wagtailConfig.CSRF_HEADER_NAME]: wagtailConfig.CSRF_TOKEN,
        },
        body: JSON.stringify({
          arguments: {
            vector_index: this.vectorIndexValue,
            // Exclude PKs for the current page, any
            // items that have already been suggested, and any
            // items that are already in the formset
            exclude_pks: [
              this.instancePkValue,
              ...this.seenPksValue,
              ...this.getFormsetChildIds(),
            ],
            content: innerText,
            limit: limit,
            chunk_size: this.hasChunkSizeValue
              ? this.chunkSizeValue
              : undefined,
          },
        }),
        signal: this.abortController?.signal,
      });
      if (!response.ok) {
        throw new Error(
          `Error fetching AI response: ${response.status} ${response.statusText}`,
        );
      }
      return await response.json().then(({ data }) => data);
    } catch (error) {
      console.error('Error fetching AI response:', error);
      throw error;
    }
  }

  clearSuggestions() {
    const suggestions = this.element.querySelectorAll(
      `[data-${this.identifier}-suggested="true"]`,
    );
    suggestions.forEach((el) => el.remove());
    this.panelComponent.totalFormsInput.val(
      this.panelComponent.formCount - suggestions.length,
    );
  }

  getFormsetChildIds() {
    const forms = Array.from(
      this.panelComponent.formsElt[0].querySelectorAll(
        ':scope > [data-inline-panel-child]:not(.deleted)',
      ),
    );
    return forms.map(
      (el: HTMLElement, idx: number) =>
        el.querySelector<HTMLInputElement>(
          `#${this.panelComponent.opts.formsetPrefix}-${idx}-related_page`,
        )?.value,
    );
  }

  updateControlStates() {
    const maxForms = this.panelComponent.opts.maxForms;
    const atLimit = maxForms && this.panelComponent.getChildCount() >= maxForms;
    const noMoreSuggestions =
      this.stateValue === ChooserSuggestionState.NO_MORE;

    if (atLimit || noMoreSuggestions) {
      this.suggestButtonTarget.disabled = true;
    } else {
      this.suggestButtonTarget.disabled = false;
    }

    // Delegate state of component-managed buttons
    // to panel component
    this.panelComponent.updateControlStates();
  }

  async suggest() {
    this.abortController = new AbortController();
    this.stateValue = ChooserSuggestionState.LOADING;

    try {
      const suggestions = await this.getSuggestions();
      this.clearSuggestions();

      if (suggestions && suggestions.length > 0) {
        suggestions.forEach((item: any) => {
          this.seenPksValue.push(item.id);
          this.addItem(item);
        });
        this.stateValue = ChooserSuggestionState.SUGGESTED;
      } else {
        this.stateValue = ChooserSuggestionState.NO_MORE;
      }
      this.updateControlStates();
    } catch (error) {
      if (this.abortController?.signal.aborted) {
        this.stateValue = ChooserSuggestionState.INITIAL;
        this.abortController = null;
        return;
      }
      console.error('Error parsing AI response:', error);
      this.stateValue = ChooserSuggestionState.ERROR;
      return;
    }
  }

  async cancel() {
    this.abortController?.abort('Cancelled by user');
  }

  async clear() {
    this.stateValue = ChooserSuggestionState.INITIAL;
    this.seenPksValue.length = 0;
    this.clearSuggestions();
    this.updateControlStates();
  }
}

window.wagtail.app.register('wai-chooser-panel', ChooserPanelController);
