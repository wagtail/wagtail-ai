import type { ApiUrlName, Prompt, WagtailAiConfiguration } from './custom';

class APIRequestError extends Error {}

export const getAIConfiguration = (): WagtailAiConfiguration => {
  const configurationElement =
    document.querySelector<HTMLScriptElement>('#wagtail-ai-config');
  if (!configurationElement || !configurationElement.textContent) {
    throw new Error('No wagtail-ai configuration found.');
  }

  try {
    return JSON.parse(configurationElement.textContent);
  } catch (err) {
    throw new SyntaxError(
      `Error parsing wagtail-ai configuration: ${err.message}`,
    );
  }
};

// TODO rename
export const fetchAIResponse = async (
  text: string,
  prompt: Prompt,
  signal: AbortSignal,
): Promise<string> => {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('prompt', prompt.uuid);
  return fetchResponse('TEXT_COMPLETION', formData, signal);
};

export const fetchResponse = async (
  action: keyof typeof ApiUrlName,
  body: FormData,
  signal?: AbortSignal,
): Promise<string> => {
  try {
    const urls = getAIConfiguration().urls;
    const res = await fetch(urls[action], { method: 'POST', body, signal });
    const json = await res.json();
    if (res.ok) {
      return json.message;
    } else {
      throw new APIRequestError(json.error);
    }
  } catch (err) {
    throw new APIRequestError(err.message);
  }
};