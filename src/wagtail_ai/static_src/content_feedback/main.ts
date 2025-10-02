import { Controller } from '@hotwired/stimulus';
import './main.css';
import { getPreviewContent } from '../preview';

interface ImprovementItem {
  original_text: string;
  suggested_text: string;
  explanation: string;
}

interface FeedbackResult {
  quality_score: FeedbackScore;
  qualitative_feedback: string[];
  specific_improvements: ImprovementItem[];
}

enum FeedbackScore {
  UNKNOWN = 0,
  NEEDS_MAJOR_IMPROVEMENT = 1,
  ADEQUATE = 2,
  EXCELLENT = 3,
}

enum FeedbackState {
  IDLE = 'idle',
  LOADING = 'loading',
  ERROR = 'error',
  SUGGESTING = 'suggesting',
}

class FeedbackController extends Controller {
  static targets = [
    'feedback',
    'feedbackItemTemplate',
    'status',
    'suggest',
    'suggestions',
    'suggestionItemTemplate',
  ];

  static values = {
    score: { default: FeedbackScore.UNKNOWN, type: Number },
    state: { default: FeedbackState.IDLE, type: String },
    temperature: { default: 1.0, type: Number },
    topK: { default: 3, type: Number },
    url: { default: '', type: String },
  };

  static languageNames = new Intl.DisplayNames(['en'], {
    type: 'language',
  });

  declare feedbackTarget: HTMLElement;
  declare feedbackItemTemplateTarget: HTMLTemplateElement;
  declare statusTarget: HTMLElement;
  declare suggestTarget: HTMLButtonElement;
  declare suggestionsTarget: HTMLElement;
  declare suggestionItemTemplateTarget: HTMLTemplateElement;
  declare scoreValue: FeedbackScore;
  declare stateValue: FeedbackState;
  declare temperatureValue: number;
  declare topKValue: number;
  declare urlValue: string;
  declare form: HTMLFormElement;
  declare walker: TreeWalker;
  targetText = '';
  abortController: AbortController | null = null;
  suggestionFields: Record<string, HTMLElement> = {};

  /** A cached LanguageModel instance Promise to avoid recreating it unnecessarily. */
  #session: any = null;
  contentLanguage = document.documentElement.lang || 'en';
  editorLanguage = document.documentElement.lang || 'en';
  contentLanguageLabel = FeedbackController.languageNames.of(
    this.contentLanguage,
  );
  editorLanguageLabel = FeedbackController.languageNames.of(
    this.editorLanguage,
  );

  /** Promise of a browser LanguageModel instance. */
  get session() {
    if (!('LanguageModel' in window)) return null;
    if (this.#session) return this.#session; // Return from cache
    return this.createModel();
  }

  get schema() {
    return {
      type: 'object',
      properties: {
        quality_score: {
          type: 'integer',
          enum: [1, 2, 3],
          description:
            'Content quality score (1=needs major improvement, 2=adequate, 3=excellent)',
        },
        qualitative_feedback: {
          type: 'array',
          items: { type: 'string' },
          description: `3-5 bullet points of qualitative feedback in language: "${this.editorLanguageLabel}"`,
          minItems: 3,
          maxItems: 5,
        },
        specific_improvements: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              original_text: {
                type: 'string',
                description: 'The original text that needs improvement',
              },
              suggested_text: {
                type: 'string',
                description: `The suggested revised text. Translate the text to ${this.contentLanguageLabel} if necessary. The text MUST be in ${this.contentLanguageLabel}.`,
              },
              explanation: {
                type: 'string',
                description: `Brief explanation in ${this.editorLanguageLabel} of why this change improves the content.`,
              },
            },
            additionalProperties: false,
            required: ['original_text', 'suggested_text', 'explanation'],
          },
          description: `Specific text improvements with original and suggested versions in ${this.contentLanguageLabel}.`,
          minItems: 1,
        },
      },
      additionalProperties: false,
      required: [
        'quality_score',
        'qualitative_feedback',
        'specific_improvements',
      ],
    };
  }

  connect() {
    this.generate = this.generate.bind(this);
    this.scoreValue = FeedbackScore.UNKNOWN;
    this.stateValue = FeedbackState.IDLE;
    this.form = document.querySelector<HTMLFormElement>('[data-edit-form]')!;
    this.walker = this.createWalker();
  }

  createWalker() {
    return document.createTreeWalker(
      this.form,
      NodeFilter.SHOW_ELEMENT,
      (el: HTMLInputElement | HTMLTextAreaElement | HTMLElement) => {
        const isInput =
          el instanceof HTMLInputElement ||
          el instanceof HTMLTextAreaElement ||
          el.isContentEditable;
        if (!isInput || el.getAttribute('type') === 'hidden')
          return NodeFilter.FILTER_SKIP;

        const text = ('value' in el ? el.value : el.innerText)
          // Normalize whitespace to avoid mismatches
          .replace(/\s+/g, ' ')
          .trim();

        return text.includes(this.targetText)
          ? NodeFilter.FILTER_ACCEPT
          : NodeFilter.FILTER_SKIP;
      },
    );
  }

  createModel() {
    const initialPrompts = [
      {
        role: 'system',
        content:
          'You are a helpful assistant that responds with structured data according to the provided schema. The language rules specified are IMPORTANT. Always ensure the feedback and improvements are in the correct language.',
      },
      {
        role: 'user',
        content: `Analyze the given content and provide:
1. A quality score between 1 and 3 (1=needs major improvement, 2=adequate, 3=excellent)
2. 3-5 bullet points of qualitative feedback highlighting strengths and areas for improvement in ${this.editorLanguageLabel}
3. Specific text improvements with original text, suggested revised text in ${this.contentLanguageLabel}, and a brief explanation
   in ${this.editorLanguageLabel} for why each change would improve the content

The language rules specified are IMPORTANT. Always ensure the feedback and improvements are in the correct language.

Return JSON with the provided structure WITHOUT the markdown code block. Start immediately with a { character and end with a } character.`,
      },
    ];

    this.#session = window.LanguageModel.create({
      temperature: this.temperatureValue,
      topK: this.topKValue,
      initialPrompts,
      monitor: (m: EventTarget) => {
        m.addEventListener(
          'downloadprogress',
          (event: Event & { loaded: number; total: number }) => {
            const label = this.suggestTarget.lastElementChild!;
            const { loaded, total } = event;
            if (loaded === total) {
              if (this.suggestTarget.disabled) {
                label.textContent = 'Generating…';
              } else {
                label.textContent = 'Generate suggestions';
              }
              return;
            }
            const percent = Math.round((loaded / total) * 100);
            label.textContent = `Loading AI… ${percent}%`;
          },
        );
      },
    });
    return this.#session;
  }

  temperatureValueChanged(newValue: number, oldValue: number) {
    if (oldValue && oldValue != newValue) this.createModel();
  }

  topKValueChanged(newValue: number, oldValue: number) {
    if (oldValue && oldValue != newValue) this.createModel();
  }

  scoreValueChanged() {
    // TooltipController won't change the content if the old value is falsy
    let scoreText = '-';

    switch (this.scoreValue) {
      case FeedbackScore.NEEDS_MAJOR_IMPROVEMENT:
        scoreText = gettext('Quality: needs major improvement');
        break;
      case FeedbackScore.ADEQUATE:
        scoreText = gettext('Quality: adequate');
        break;
      case FeedbackScore.EXCELLENT:
        scoreText = gettext('Quality: excellent');
        break;
      default:
        break;
    }
    this.statusTarget.setAttribute('data-w-tooltip-content-value', scoreText);
  }

  reset() {
    this.scoreValue = FeedbackScore.UNKNOWN;
    this.stateValue = FeedbackState.IDLE;
    this.abortController?.abort('Cancelled by user');
    this.feedbackTarget.innerHTML = '';
    this.suggestionsTarget.innerHTML = '';
    this.suggestionFields = {};
  }

  dismissItem(event: Event) {
    (event.target as HTMLElement).closest('li')!.remove();
    if (!this.element.querySelector('li')) this.reset();
  }

  showSuggestion(event: Event) {
    const button = event.target as HTMLElement;
    const suggestionId = button.getAttribute('data-suggestion-id')!;
    const field = this.suggestionFields[suggestionId];
    field?.scrollIntoView({ behavior: 'smooth' });
    // Highlight the original text in the editor using the browser's
    // text fragment feature.
    // Unfortunately, there is no way to remove the highlight once added, other
    // than the user manually right-clicking the highlighted text and choosing
    // "Remove highlight", or by reloading the page.
    // const originalText = button
    //   .closest('li')!
    //   .querySelector<HTMLElement>(
    //     '[data-template-key="original_text"]',
    //   )!.innerText;
    // const encoded = encodeURIComponent(originalText).replace(
    // 	/[-&,]/g,
    // 	(c) => '%' + c.charCodeAt(0).toString(16).toUpperCase()
    // );
    // window.location.hash = `#:~:text=${encoded}`;
  }

  async renderFeedback(feedback: string) {
    const item =
      this.feedbackItemTemplateTarget.content.firstElementChild!.cloneNode(
        true,
      ) as HTMLElement;
    item.querySelector('[data-template-key="text"]')!.textContent = feedback;
    this.feedbackTarget.appendChild(item);
  }

  async renderSuggestion(suggestion: ImprovementItem, index: number) {
    const suggestionId = `suggestion-${index}`;
    const item =
      this.suggestionItemTemplateTarget.content.firstElementChild!.cloneNode(
        true,
      ) as HTMLElement;

    const suggestionElement = item.querySelector<HTMLTextAreaElement>(
      '[data-template-key="suggested_text"]',
    )!;
    suggestionElement.name = suggestionId;
    suggestionElement.textContent = suggestion.suggested_text;
    suggestionElement.setAttribute(
      'data-w-tooltip-content-value',
      suggestion.explanation,
    );

    // Find the field containing the original text and store it for later use.
    this.walker.currentNode = this.form;
    this.targetText = suggestion.original_text;
    while (this.walker.nextNode()) {
      const node = this.walker.currentNode as HTMLElement;
      if (node) {
        this.suggestionFields[suggestionId] = node;
        break;
      }
    }

    // If we found field for the original text, set the suggestion ID on it.
    // Otherwise, remove the button.
    const showButton = item.querySelector<HTMLElement>('[data-suggestion-id]')!;
    if (this.suggestionFields[suggestionId]) {
      showButton.setAttribute('data-suggestion-id', suggestionId);
    } else {
      showButton.hidden = true;
    }

    this.suggestionsTarget.appendChild(item);
    // Auto-resize the textarea to fit content. This must be done after it's
    // been added to the DOM to get correct scrollHeight.
    suggestionElement.style.height = suggestionElement.scrollHeight + 'px';
  }

  async prompt(): Promise<FeedbackResult> {
    const previewContent = await getPreviewContent();
    if (!previewContent) {
      throw new Error('Unable to get page content for analysis.');
    }

    const { innerText, innerHTML, lang } = previewContent;
    this.contentLanguage = lang;
    this.contentLanguageLabel = FeedbackController.languageNames.of(
      this.contentLanguage,
    );

    // If a server endpoint is configured, use that.
    if (this.urlValue) {
      try {
        const response = await fetch(this.urlValue, {
          method: 'POST',
          headers: {
            [wagtailConfig.CSRF_HEADER_NAME]: wagtailConfig.CSRF_TOKEN,
          },
          body: JSON.stringify({
            arguments: {
              content_text: innerText.trim(),
              content_html: innerHTML.trim(),
              content_language: this.contentLanguageLabel,
              editor_language: this.editorLanguageLabel,
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

    // Otherwise, use the in-browser model.
    const session = await this.session;
    await session.append([
      {
        role: 'user',
        content: 'Content to analyze and improve:\n\n' + innerText,
      },
    ]);
    return JSON.parse(
      await session.prompt(innerText, {
        responseConstraint: this.schema,
        signal: this.abortController?.signal,
      }),
    );
  }

  async generate() {
    this.reset();
    this.abortController = new AbortController();
    this.stateValue = FeedbackState.LOADING;

    try {
      const data = await this.prompt();
      if (!data?.quality_score) {
        throw new Error('Invalid response from AI model');
      }

      this.scoreValue = data.quality_score;
      data.qualitative_feedback.forEach((feedback) => {
        this.renderFeedback(feedback);
      });
      data.specific_improvements.forEach((suggestion, index) => {
        this.renderSuggestion(suggestion, index);
      });
    } catch (error) {
      if (this.abortController?.signal.aborted) {
        this.stateValue = FeedbackState.IDLE;
        this.abortController = null;
        return;
      }
      console.error('Error parsing AI response:', error);
      this.stateValue = FeedbackState.ERROR;
      return;
    }

    this.stateValue = FeedbackState.SUGGESTING;
  }
}

window.wagtail.app.register('wai-feedback', FeedbackController);
