import './main.css';
import AIControl from './AIControl';

declare global {
  interface Window {
    draftail: any;
    Draftail: any;
  }
}

window.draftail.registerPlugin(
  {
    type: 'ai',
    inline: AIControl,
  },
  'controls',
);
