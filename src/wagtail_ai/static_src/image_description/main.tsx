import './main.css';
import { fetchResponse } from '../api';

import wandIcon from '!!raw-loader!../wand_icon.svg';

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
  button.title = input.dataset['wagtailai-button-title'] || '';
  button.classList.add('wagtailai-button');
  button.innerHTML = wandIcon;
  flexWrapper.appendChild(button);

  let errorMessage: HTMLElement | null = null;

  button.addEventListener('click', async () => {
    errorMessage?.parentNode?.removeChild(errorMessage);
    button.disabled = true;
    button.classList.add('loading');

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

    button.classList.remove('loading');
    button.disabled = false;
  });
});
