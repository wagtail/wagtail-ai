import './main.css';
import { fetchResponse } from '../api';

import { Controller } from '@hotwired/stimulus';

class DescribeController extends Controller<HTMLElement | HTMLInputElement> {
  static classes = ['loading'];
  static targets = ['button', 'error', 'input'];
  static values = {
    file: String,
    imageId: String,
  };

  declare loadingClass: string;
  declare buttonTarget: HTMLButtonElement;
  declare errorTarget: HTMLParagraphElement;
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
    this.errorTarget.hidden = true;
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
      this.errorTarget.hidden = false;
    }

    this.element.classList.remove(this.loadingClass);
    this.buttonTarget.disabled = false;
  }
}

window.wagtail.app.register('wai-describe', DescribeController);
