import './main.css';
import { fetchResponse, APIRequestError } from '../api';

import { Controller } from '@hotwired/stimulus';

class DescribeController extends Controller<HTMLElement | HTMLInputElement> {
  static classes = ['loading'];
  static targets = ['button', 'error', 'errorTemplate', 'input'];
  static values = {
    file: String,
    imageId: String,
  };

  declare loadingClass: string;
  declare buttonTarget: HTMLButtonElement;
  declare errorTarget: HTMLParagraphElement;
  declare errorTemplateTarget: HTMLTemplateElement;
  declare inputTarget: HTMLInputElement;
  declare hasFileValue: boolean;
  declare fileValue: string;
  declare hasImageIdValue: boolean;
  declare imageIdValue: string;

  fileInput: HTMLInputElement | null = null;

  get form() {
    return 'form' in this.element
      ? this.element.form!
      : this.element.closest('form')!;
  }

  fileValueChanged(newValue: string) {
    this.fileInput = this.form.querySelector<HTMLInputElement>(newValue);
  }

  async describe() {
    this.errorTarget.innerHTML = '';
    this.buttonTarget.disabled = true;
    this.element.classList.add(this.loadingClass);

    try {
      const formData = new FormData();
      if (this.hasImageIdValue) {
        formData.append('image_id', this.imageIdValue);
      }
      if (this.fileInput?.files?.[0]) {
        formData.append('file', this.fileInput.files[0]);
      }
      const maxLength = this.inputTarget.getAttribute('maxlength');
      if (maxLength) {
        formData.append('maxlength', maxLength);
      }
      this.inputTarget.value = await fetchResponse('DESCRIBE_IMAGE', formData);
    } catch (error) {
      const errorMessage =
        this.errorTemplateTarget.content.firstElementChild!.cloneNode(true);
      if (error instanceof APIRequestError) {
        // Error message from the API is user-friendly,
        // show that instead of the generic one from the template.
        errorMessage.textContent = error.message;
      }
      this.errorTarget.appendChild(errorMessage);
    }

    this.element.classList.remove(this.loadingClass);
    this.buttonTarget.disabled = false;
  }
}

window.wagtail.app.register('wai-describe', DescribeController);
