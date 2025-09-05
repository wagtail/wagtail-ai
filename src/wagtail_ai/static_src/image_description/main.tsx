import './main.css';
import { fetchResponse } from '../api';

import wandIcon from '../wand_icon.svg';

document.addEventListener('wagtail-ai:image-form', (event) => {
  const input = event.target as HTMLInputElement;
  const imageId = input.dataset.wagtailaiImageId;
  if (!imageId) {
    throw new Error('The attribute data-wagtailai-image-id is missing.');
  }
  if (!input.form) {
    throw new Error('The input is not part of a form.');
  }

  const inputParent = input.parentNode!;
  const flexWrapper = document.createElement('div');
  flexWrapper.classList.add('wagtailai-input-wrapper');
  inputParent.replaceChild(flexWrapper, input);
  flexWrapper.appendChild(input);

  const button = document.createElement('button');
  button.type = 'button';
  button.title = input.dataset.wagtailaiButtonTitle || '';
  button.classList.add('button', 'wagtailai-button');
  button.innerHTML = wandIcon;
  flexWrapper.appendChild(button);

  const maxLength = input.getAttribute('maxlength');

  let errorMessage: HTMLParagraphElement | null = null;

  button.addEventListener('click', async () => {
    errorMessage?.parentNode?.removeChild(errorMessage);
    button.disabled = true;
    button.classList.add('loading');

    try {
      const formData = new FormData();
      formData.append('image_id', imageId);
      if (maxLength) {
        formData.append('maxlength', maxLength);
      }
      input.value = await fetchResponse('DESCRIBE_IMAGE', formData);
    } catch (error) {
      errorMessage = document.createElement('p');
      errorMessage.classList.add('error-message');
      errorMessage.textContent = 'Could not generate image description.';
      inputParent.append(errorMessage);
    }

    button.classList.remove('loading');
    button.disabled = false;
  });
});
