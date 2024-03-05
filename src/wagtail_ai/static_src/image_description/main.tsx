import './main.css';
import { fetchResponse } from '../api';

// TODO find a way to import the same SVG file here and in WandIcon.tsx
const wandIcon = `<svg
  width="16"
  height="16"
  className="Draftail-Icon"
  aria-hidden="true"
  viewBox="0 0 576 512"
>
  <path d="M234.7 42.7L197 56.8c-3 1.1-5 4-5 7.2s2 6.1 5 7.2l37.7 14.1L248.8 123c1.1 3 4 5 7.2 5s6.1-2 7.2-5l14.1-37.7L315 71.2c3-1.1 5-4 5-7.2s-2-6.1-5-7.2L277.3 42.7 263.2 5c-1.1-3-4-5-7.2-5s-6.1 2-7.2 5L234.7 42.7zM46.1 395.4c-18.7 18.7-18.7 49.1 0 67.9l34.6 34.6c18.7 18.7 49.1 18.7 67.9 0L529.9 116.5c18.7-18.7 18.7-49.1 0-67.9L495.3 14.1c-18.7-18.7-49.1-18.7-67.9 0L46.1 395.4zM484.6 82.6l-105 105-23.3-23.3 105-105 23.3 23.3zM7.5 117.2C3 118.9 0 123.2 0 128s3 9.1 7.5 10.8L64 160l21.2 56.5c1.7 4.5 6 7.5 10.8 7.5s9.1-3 10.8-7.5L128 160l56.5-21.2c4.5-1.7 7.5-6 7.5-10.8s-3-9.1-7.5-10.8L128 96 106.8 39.5C105.1 35 100.8 32 96 32s-9.1 3-10.8 7.5L64 96 7.5 117.2zm352 256c-4.5 1.7-7.5 6-7.5 10.8s3 9.1 7.5 10.8L416 416l21.2 56.5c1.7 4.5 6 7.5 10.8 7.5s9.1-3 10.8-7.5L480 416l56.5-21.2c4.5-1.7 7.5-6 7.5-10.8s-3-9.1-7.5-10.8L480 352l-21.2-56.5c-1.7-4.5-6-7.5-10.8-7.5s-9.1 3-10.8 7.5L416 352l-56.5 21.2z" />
</svg>`;

document.addEventListener('wagtail-ai:image-form', (event) => {
  const input = event.target as HTMLInputElement;
  const imageId = input.dataset['wagtailai-image-id']!;
  const csrfToken = (
    input.form!.querySelector(
      'input[name=csrfmiddlewaretoken]',
    ) as HTMLInputElement
  ).value;

  const flexWrapper = document.createElement('div');
  flexWrapper.classList.add('wagtailai-input-wrapper');
  input.parentNode!.replaceChild(flexWrapper, input);
  flexWrapper.appendChild(input);

  const button = document.createElement('button');
  button.type = 'button';
  button.classList.add('wagtailai-button');
  button.innerHTML = wandIcon;
  flexWrapper.appendChild(button);

  let errorMessage: HTMLElement | null = null;

  button.addEventListener('click', async () => {
    errorMessage?.parentNode?.removeChild(errorMessage);
    button.disabled = true;
    button.innerText = '…';

    try {
      const formData = new FormData();
      formData.append('image_id', imageId);
      formData.append('csrfmiddlewaretoken', csrfToken);
      input.value = await fetchResponse('DESCRIBE_IMAGE', formData);
    } catch (error) {
      errorMessage = document.createElement('p');
      errorMessage.classList.add('error-message');
      errorMessage.textContent = 'Could not generate image description.';
      flexWrapper.parentNode!.append(errorMessage);
    }

    button.innerHTML = wandIcon;
    button.disabled = false;
  });
});
