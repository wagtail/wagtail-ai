import { Controller } from '@hotwired/stimulus';
import './main.css';

interface PreviewController extends Controller {
  extractContent: () => Promise<{
    innerHTML: string;
    innerText: string;
    lang: string;
  }>;
}

interface ImprovementItem {
  originalText: string;
  suggestedText: string;
  explanation: string;
}

interface FeedbackResult {
  qualityScore: FeedbackStatus;
  qualitativeFeedback: string[];
  specificImprovements: ImprovementItem[];
}

enum FeedbackStatus {
  NEEDS_MAJOR_IMPROVEMENT = 1,
  ADEQUATE = 2,
  EXCELLENT = 3,
}

class FeedbackController extends Controller {
  static targets = [
    'clear',
    'feedback',
    'feedbackItemTemplate',
    'spinner',
    'status',
    'suggest',
    'suggestions',
    'suggestionItemTemplate',
  ];

  static values = {
    temperature: { default: 1.0, type: Number },
    topK: { default: 3, type: Number },
  };

  static status: Record<FeedbackStatus, string> = {
    1: '🔴',
    2: '🟠',
    3: '🟢',
  };

  static languageNames = new Intl.DisplayNames(['en'], {
    type: 'language',
  });

  static get shouldLoad() {
    return 'LanguageModel' in window;
  }

  declare clearTarget: HTMLElement;
  declare feedbackTarget: HTMLElement;
  declare feedbackItemTemplateTarget: HTMLTemplateElement;
  declare spinnerTarget: HTMLElement;
  declare statusTarget: HTMLElement;
  declare suggestTarget: HTMLButtonElement;
  declare suggestionsTarget: HTMLElement;
  declare suggestionItemTemplateTarget: HTMLTemplateElement;
  declare temperatureValue: number;
  declare topKValue: number;
  declare form: HTMLFormElement;
  declare walker: TreeWalker;
  targetText = '';

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
    if (this.#session) return this.#session; // Return from cache
    return this.createModel();
  }

  get suggestLabel() {
    return this.suggestTarget.lastElementChild!;
  }

  get schema() {
    return {
      type: 'object',
      properties: {
        qualityScore: {
          type: 'integer',
          enum: [1, 2, 3],
          description:
            'Content quality score (1=needs major improvement, 2=adequate, 3=excellent)',
        },
        qualitativeFeedback: {
          type: 'array',
          items: { type: 'string' },
          description: `3-5 bullet points of qualitative feedback in language: "${this.editorLanguageLabel}"`,
          minItems: 3,
          maxItems: 5,
        },
        specificImprovements: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              originalText: {
                type: 'string',
                description: 'The original text that needs improvement',
              },
              suggestedText: {
                type: 'string',
                description: `The suggested revised text. Translate the text to ${this.contentLanguageLabel} if necessary. The text MUST be in ${this.contentLanguageLabel}.`,
              },
              explanation: {
                type: 'string',
                description: `Brief explanation in ${this.editorLanguageLabel} of why this change improves the content.`,
              },
            },
            additionalProperties: false,
            required: ['originalText', 'suggestedText', 'explanation'],
          },
          description: `Specific text improvements with original and suggested versions in ${this.contentLanguageLabel}.`,
          minItems: 1,
        },
      },
      additionalProperties: false,
      required: ['qualityScore', 'qualitativeFeedback', 'specificImprovements'],
    };
  }

  connect() {
    this.generate = this.generate.bind(this);
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
      //       {
      //         role: 'user',
      //         content: `Bread is like, you kno, that thing ppl eat all over, it's made of flur and water and stuf, and somtimes yeast or maybe not, but anywy it comes in alot of shapes like round, or long, or just like sliced in bags at the stor. People eat it with butter or sandwhiches or tost or whatever, and some bread is soft but others are hard and cruncy, but basicly it's just bread and peple like it becuz it's food and fills you up.`,
      //       },
      //       {
      //         role: 'assistant',
      //         content: `Here are some suggestions to improve the content:

      // - **Clarify tone and style**: Remove filler words (“like,” “you kno,” “whatever”) and make the writing more professional and concise.
      // - **Fix spelling and grammar**: Correct typos such as “flur,” “stuf,” “sandwhiches,” “tost,” “becuz,” and “peple.”
      // - **Add structure**: Organize into short sentences or bullet points for readability.
      // - **Enrich details**: Mention different bread types (sourdough, rye, flatbread) and cultural significance.
      // - **Improve flow**: Transition smoothly between preparation, forms, uses, and why people enjoy it.
      // - **Refine conclusion**: Replace “it's just bread and people like it becuz it's food” with a more thoughtful closing about bread's role in daily life.`,
      //       },
    ];
    // eslint-disable-next-line no-undef
    this.#session = window.LanguageModel.create({
      temperature: this.temperatureValue,
      topK: this.topKValue,
      initialPrompts,
      monitor: (m: EventTarget) => {
        m.addEventListener(
          'downloadprogress',
          (event: Event & { loaded: number; total: number }) => {
            const label = this.suggestLabel;
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

  clear() {
    this.statusTarget.textContent = '';
    this.feedbackTarget.innerHTML = '';
    this.feedbackTarget.hidden = true;
    (this.feedbackTarget.previousElementSibling as HTMLElement).hidden = true;
    this.suggestionsTarget.innerHTML = '';
    this.suggestionsTarget.hidden = true;
    (this.suggestionsTarget.previousElementSibling as HTMLElement).hidden =
      true;
    this.clearTarget.hidden = true;
  }

  dismissItem(event: Event) {
    (event.target as HTMLElement).closest('li')!.remove();
  }

  showFeedback(event: Event) {
    const originalText = (event.target as HTMLElement)
      .closest('li')!
      .querySelector<HTMLElement>(
        '[data-template-key="originalText"]',
      )!.innerText;
    // Highlight the original text in the editor using the browser's
    // text fragment feature.
    // Unfortunately, there is no way to remove the highlight once added, other
    // than the user manually right-clicking the highlighted text and choosing
    // "Remove highlight", or by reloading the page.
    // const encoded = encodeURIComponent(originalText).replace(
    // 	/[-&,]/g,
    // 	(c) => '%' + c.charCodeAt(0).toString(16).toUpperCase()
    // );
    // window.location.hash = `#:~:text=${encoded}`;
    this.walker.currentNode = this.form;
    this.targetText = originalText;
    while (this.walker.nextNode()) {
      const node = this.walker.currentNode as HTMLElement;
      if (node) {
        node.scrollIntoView({ behavior: 'smooth' });
        return;
      }
    }
  }

  async renderFeedback(feedback: string) {
    const item =
      this.feedbackItemTemplateTarget.content.firstElementChild!.cloneNode(
        true,
      ) as HTMLElement;
    item.querySelector('[data-template-key="text"]')!.textContent = feedback;
    this.feedbackTarget.appendChild(item);
  }

  async renderSuggestion(suggestion: ImprovementItem) {
    const item =
      this.suggestionItemTemplateTarget.content.firstElementChild!.cloneNode(
        true,
      ) as HTMLElement;
    const data = ['originalText', 'suggestedText', 'explanation'] as const;
    data.forEach((key) => {
      const element = item.querySelector(`[data-template-key="${key}"]`)!;
      element.textContent = suggestion[key];
    });
    this.suggestionsTarget.appendChild(item);
  }

  async getPageContent() {
    const previewController = window.wagtail.app.queryController(
      'w-preview',
    ) as PreviewController;
    const { innerText, lang } = await previewController.extractContent();
    this.contentLanguage = lang;
    this.contentLanguageLabel = FeedbackController.languageNames.of(
      this.contentLanguage,
    );
    return innerText;
  }

  async generate() {
    this.clear();
    const label = this.suggestLabel;
    label.textContent = 'Generating…';
    this.suggestTarget.disabled = true;
    this.suggestTarget
      .querySelector('svg use')!
      .setAttribute('href', '#icon-wand-animated');
    this.spinnerTarget.hidden = false;

    const text = await this.getPageContent();
    const session = await this.session;
    await session.append([
      {
        role: 'user',
        content: 'Content to analyze and improve:\n\n' + text,
      },
    ]);
    let result = await session.prompt(text, {
      responseConstraint: this.schema,
    });
    try {
      const data: FeedbackResult = JSON.parse(result);
      if (data.qualityScore) {
        this.statusTarget.textContent =
          FeedbackController.status[data.qualityScore];
        this.feedbackTarget.hidden = false;
        (this.feedbackTarget.previousElementSibling as HTMLElement).hidden =
          false;
        data.qualitativeFeedback.forEach((feedback) => {
          this.renderFeedback(feedback);
        });
        this.suggestionsTarget.hidden = false;
        (this.suggestionsTarget.previousElementSibling as HTMLElement).hidden =
          false;
        data.specificImprovements.forEach((suggestion) => {
          this.renderSuggestion(suggestion);
        });
      } else {
        this.renderFeedback('Invalid response format');
      }
    } catch (error) {
      console.error('Error parsing AI response:', error);
    }

    this.spinnerTarget.hidden = true;
    this.suggestTarget.disabled = false;
    this.clearTarget.hidden = false;
    label.textContent = 'Generate suggestions';
    this.suggestTarget
      .querySelector('svg use')!
      .setAttribute('href', '#icon-wand');
  }
}

window.wagtail.app.register('wai-feedback', FeedbackController);
