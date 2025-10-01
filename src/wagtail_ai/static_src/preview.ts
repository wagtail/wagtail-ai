import type { Controller } from '@hotwired/stimulus';

export interface PreviewContent {
  lang: string;
  innerText: string;
  innerHTML: string;
}

export interface PreviewController extends Controller {
  ready: boolean;
  checkAndUpdatePreview: () => Promise<boolean | undefined>;
  extractContent: () => Promise<PreviewContent | null>;
}

export async function getPreviewContent() {
  const preview =
    window.wagtail.app.queryController<PreviewController>('w-preview');
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
