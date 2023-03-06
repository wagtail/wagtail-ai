import './main.css';
import { ControlControl } from 'draftail';
import AIControl from './AIControl';

declare global {
  interface Window {
    draftail: any;
  }
}

const control: ControlControl = {
  type: 'inline',
  label: 'AI Completion',
  inline: AIControl,
};

const initEditorProxy = new Proxy(window.draftail.initEditor, {
  apply: (target, _, argumentsList) => {
    argumentsList[1].controls = [control];
    return target(...argumentsList);
  },
});
window.draftail.initEditor = initEditorProxy;
