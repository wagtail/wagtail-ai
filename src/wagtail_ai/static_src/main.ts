import './main.css';

const configurationElement =
  document.querySelector<HTMLScriptElement>('#wagtail-ai-config');
if (!configurationElement || !configurationElement.textContent) {
  throw new Error('No wagtail-ai configuration found.');
}

try {
  const config = JSON.parse(configurationElement.textContent);
  window.wagtailAI = { ...window.wagtailAI, config };
} catch (err) {
  throw new SyntaxError(
    `Error parsing wagtail-ai configuration: ${err.message}`,
  );
}
