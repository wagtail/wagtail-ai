import './main.css';
import { fetchResponse } from '../api';

import { Controller } from '@hotwired/stimulus';

class DescribeController extends Controller<HTMLInputElement> {
  static classes = ['loading'];
  static targets = ['button', 'error', 'input'];
  static values = {
    imageId: String,
  };

  declare loadingClass: string;
  declare buttonTarget: HTMLButtonElement;
  declare errorTarget: HTMLParagraphElement;
  declare inputTarget: HTMLInputElement;
  declare imageIdValue: string;

  async describe() {
    this.errorTarget.hidden = true;
    this.buttonTarget.disabled = true;
    this.element.classList.add(this.loadingClass);

    try {
      const formData = new FormData();
      formData.append('image_id', this.imageIdValue);
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
