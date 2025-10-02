import { Controller } from '@hotwired/stimulus';
import './main.css';

interface PreviewController extends Controller {
  extractContent: () => Promise<{
    innerHTML: string;
    innerText: string;
    lang: string;
  }>;
}

interface PanelElement extends HTMLElement {
  _panel: any;
}

enum SuggestionState {
  IDLE = 'idle',
  LOADING = 'loading',
  ERROR = 'error',
  COMPLETE = 'complete',
}

class MultipleChooserPanelController extends Controller<PanelElement> {
  static targets = ['suggestButton'];
  static values = {
    url: {
      default: window.wagtailAI.config.urls.SIMILAR_CONTENT,
      type: String,
    },
    state: {
      default: SuggestionState.IDLE,
      type: String,
    },
    instancePk: Number,
    suggestLimit: Number,
  };
  declare urlValue: string;
  declare instancePkValue: number;
  declare suggestLimitValue: number;
  declare stateValue: SuggestionState;
  panelComponent: any;

  connect() {
    this.panelComponent = this.element._panel;
  }

  addItem(item: any) {
    const panel = this.panelComponent;
    panel.addForm();
    const formIndex = panel.formCount - 1;
    const formPrefix = `${panel.opts.formsetPrefix}-${formIndex}`;
    const chooserFieldId = `${formPrefix}-${panel.opts.chooserFieldName}`;
    const chooserWidget = panel.chooserWidgetFactory.getById(chooserFieldId);
    chooserWidget.setState({
      id: item.id,
      adminTitle: item.title,
      editUrl: item.editUrl,
    });
  }

  async getPageContent() {
    const previewController = window.wagtail.app.queryController(
      'w-preview',
    ) as PreviewController;
    const { innerText } = await previewController.extractContent();
    return innerText;
  }

  renderLoadingIndicator() {
    const loadingElement = document.createElement('div');
    loadingElement.innerHTML = 'Looking for relevant pages...';
    loadingElement.classList.add('wai-suggest-loading');
    const panelContent = this.element.querySelector('.w-panel__content');
    panelContent?.appendChild(loadingElement);
  }

  clearLoadingIndicator() {
    this.element.querySelector('.wai-suggest-loading')?.remove();
  }

  stateValueChanged() {
    if (this.stateValue === SuggestionState.LOADING) {
      this.renderLoadingIndicator();
    } else {
      this.clearLoadingIndicator();
    }
  }

  async getSimilarContent() {
    this.stateValue = SuggestionState.LOADING;
    const text = await this.getPageContent();
    await new Promise((resolve) => setTimeout(resolve, 2000));
    const res = await fetch(this.urlValue, {
      method: 'POST',
      headers: {
        [wagtailConfig.CSRF_HEADER_NAME]: wagtailConfig.CSRF_TOKEN,
      },
      body: JSON.stringify({
        arguments: {
          vector_index: 'PageIndex',
          current_page_pk: this.instancePkValue,
          limit: this.suggestLimitValue,
          content: text,
        },
      }),
    });
    const resJson = await res.json();
    resJson.data.forEach((item: any) => {
      this.addItem(item);
    });
    this.stateValue = SuggestionState.COMPLETE;
  }

  async suggest() {
    await this.getSimilarContent();
  }
}

window.wagtail.app.register(
  'wai-multiple-chooser-panel',
  MultipleChooserPanelController,
);
