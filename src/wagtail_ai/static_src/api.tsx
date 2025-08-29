import type { ApiUrlName } from './custom';

export class APIRequestError extends Error {}

export const fetchResponse = async (
  action: keyof typeof ApiUrlName,
  body: FormData,
  signal?: AbortSignal,
): Promise<string> => {
  const urls = window.wagtailAI.config.urls;
  const res = await fetch(urls[action], {
    method: 'POST',
    headers: {
      [wagtailConfig.CSRF_HEADER_NAME]: wagtailConfig.CSRF_TOKEN,
    },
    body,
    signal,
  });
  const json = await res.json();
  if (res.ok) {
    return json.message;
  } else {
    throw new APIRequestError(json.error);
  }
};
