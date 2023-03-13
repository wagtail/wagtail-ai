//import React from 'react';
import './main.css';
import { ControlComponentProps, ControlControl } from 'draftail';
import AIControl from './AIControl';
import React from 'react';

declare global {
  interface Window {
    draftail: any;
    Draftail: any;
  }
}

const control: ControlControl = {
  type: 'inline',
  label: 'AI Completion',
  inline: AIControl,
};

const initEditorProxy = new Proxy(window.draftail.initEditor, {
  apply: (target, thisArg, argumentsList) => {
    // Get the target editor in the same way initEditor does and
    // create a partially-applied AIControl component with the
    // element passed as the `field` prop so we can access
    // it later.
    const [selector, , currentScript] = argumentsList;
    const context = currentScript ? currentScript.parentNode : document.body;
    const field =
      context.querySelector(selector) || document.body.querySelector(selector);
    const PartialAIControl = (props: ControlComponentProps) => (
      <AIControl field={field} {...props} />
    );
    control.inline = PartialAIControl;
    argumentsList[1].controls = [control];
    return Reflect.apply(target, thisArg, argumentsList);
  },
});
window.draftail.initEditor = initEditorProxy;
