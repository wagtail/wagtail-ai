import { Controller } from '@hotwired/stimulus';
import './main.css';
import { getPreviewContent } from '../preview';

interface PanelElement extends HTMLElement {
  _panel: any;
}

enum SuggestionState {
  IDLE = 'idle',
  LOADING = 'loading',
  ERROR = 'error',
  SUGGESTED = 'suggested',
}

class SuggestionsPanelController extends Controller<PanelElement> {
  static values = {
    url: {
      default: window.wagtailAI.config.urls.SUGGESTED_CONTENT,
      type: String,
    },
    state: {
      default: SuggestionState.IDLE,
      type: String,
    },
    vectorIndex: String,
    instancePk: Number,
    limit: Number,
    chunkSize: Number,
  };
  declare urlValue: string;
  declare instancePkValue: number;
  declare vectorIndexValue: string;
  declare limitValue: number;
  declare stateValue: SuggestionState;
  declare chunkSizeValue: number;
  abortController: AbortController | null = null;
  panelComponent: any | null = null;

  connect() {
    this.panelComponent = this.element._panel;
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
      chooserPanel.classList.add('wai-suggestions__form-suggested');
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
            current_page_pk: this.instancePkValue,
            content: innerText,
            limit: this.limitValue,
            chunk_size: this.chunkSizeValue,
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

  async suggest() {
    this.abortController = new AbortController();
    this.stateValue = SuggestionState.LOADING;

    try {
      this.clear();
      const suggestions = await this.getSuggestions();

      suggestions.forEach((item: any) => {
        this.addItem(item);
      });
    } catch (error) {
      if (this.abortController?.signal.aborted) {
        this.stateValue = SuggestionState.IDLE;
        this.abortController = null;
        return;
      }
      console.error('Error parsing AI response:', error);
      this.stateValue = SuggestionState.ERROR;
      return;
    }

    this.stateValue = SuggestionState.SUGGESTED;
  }

  async cancel() {
    this.abortController?.abort('Cancelled by user');
  }

  async clear() {
    const suggestions = this.element.querySelectorAll(
      '.wai-suggestions__form-suggested',
    );
    suggestions.forEach((el) => el.remove());
  }
}

window.wagtail.app.register('wai-suggestions', SuggestionsPanelController);
