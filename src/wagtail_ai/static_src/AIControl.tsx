import React, { useState } from 'react';
import {
  EditorState,
  Modifier,
  SelectionState,
  ContentState,
  RichUtils,
} from 'draft-js';
import { ControlComponentProps, ToolbarButton, Icon } from 'draftail';
import { createPortal } from 'react-dom';
import { Prompt } from './custom';

class APIRequestError extends Error {}

// Generated by asking ChatGPT 'Generate a list of loading messages which mean "Loading response from AI chat bot"'...
const LOADING_MESSAGES = [
  'Processing your query, please wait...',
  'Analyzing your input, just a moment...',
  'Generating a response, hold on...',
  'Thinking, thinking, thinking...',
  'Fetching data, almost there...',
  'Compiling information, please wait...',
  'Crunching numbers, please be patient...',
  'Analyzing data, loading...',
  'Preparing response, please wait...',
  'Interpreting your message, loading...',
];

function LoadingOverlay() {
  const loadingMessage =
    LOADING_MESSAGES[Math.floor(Math.random() * LOADING_MESSAGES.length)];

  return (
    <div className="Draftail-AI-LoadingOverlay">
      <span>
        <svg className="icon icon-spinner c-spinner" aria-hidden="true">
          <use href="#icon-spinner" />
        </svg>
        {loadingMessage}
      </span>
    </div>
  );
}

function WandIcon() {
  // Font Awesome Pro 6.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc.
  return (
    <svg
      width="16"
      height="16"
      className="Draftail-Icon"
      aria-hidden="true"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 576 512"
    >
      <path d="M234.7 42.7L197 56.8c-3 1.1-5 4-5 7.2s2 6.1 5 7.2l37.7 14.1L248.8 123c1.1 3 4 5 7.2 5s6.1-2 7.2-5l14.1-37.7L315 71.2c3-1.1 5-4 5-7.2s-2-6.1-5-7.2L277.3 42.7 263.2 5c-1.1-3-4-5-7.2-5s-6.1 2-7.2 5L234.7 42.7zM46.1 395.4c-18.7 18.7-18.7 49.1 0 67.9l34.6 34.6c18.7 18.7 49.1 18.7 67.9 0L529.9 116.5c18.7-18.7 18.7-49.1 0-67.9L495.3 14.1c-18.7-18.7-49.1-18.7-67.9 0L46.1 395.4zM484.6 82.6l-105 105-23.3-23.3 105-105 23.3 23.3zM7.5 117.2C3 118.9 0 123.2 0 128s3 9.1 7.5 10.8L64 160l21.2 56.5c1.7 4.5 6 7.5 10.8 7.5s9.1-3 10.8-7.5L128 160l56.5-21.2c4.5-1.7 7.5-6 7.5-10.8s-3-9.1-7.5-10.8L128 96 106.8 39.5C105.1 35 100.8 32 96 32s-9.1 3-10.8 7.5L64 96 7.5 117.2zm352 256c-4.5 1.7-7.5 6-7.5 10.8s3 9.1 7.5 10.8L416 416l21.2 56.5c1.7 4.5 6 7.5 10.8 7.5s9.1-3 10.8-7.5L480 416l56.5-21.2c4.5-1.7 7.5-6 7.5-10.8s-3-9.1-7.5-10.8L480 352l-21.2-56.5c-1.7-4.5-6-7.5-10.8-7.5s-9.1 3-10.8 7.5L416 352l-56.5 21.2z" />
    </svg>
  );
}

const fetchAIResponse = async (
  text: string,
  prompt: Prompt,
): Promise<string> => {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('prompt', prompt.id);
  try {
    const res = await fetch(window.WAGTAIL_AI_PROCESS_URL, {
      method: 'POST',
      body: formData,
    });
    const json = await res.json();
    if (res.ok) {
      return json.message;
    } else {
      throw new APIRequestError(json.error);
    }
  } catch (err) {
    console.log('here');
    throw new APIRequestError(err.message);
  }
};

const getAllSelection = (content: ContentState): SelectionState => {
  const blockMap = content.getBlockMap();
  return new SelectionState({
    anchorKey: blockMap.first().getKey(),
    anchorOffset: 0,
    focusKey: blockMap.last().getKey(),
    focusOffset: blockMap.last().getLength(),
  });
};

const handleAppend = (
  editorState: EditorState,
  response: string,
): EditorState => {
  const newEditorState = RichUtils.insertSoftNewline(
    EditorState.moveSelectionToEnd(editorState),
  );
  const content = newEditorState.getCurrentContent();
  const nextState = Modifier.replaceText(
    content,
    EditorState.moveSelectionToEnd(newEditorState).getSelection(),
    response,
  );
  const newState = EditorState.push(
    newEditorState,
    nextState,
    'insert-characters',
  );
  return newState;
};

const handleReplace = (
  editorState: EditorState,
  response: string,
): EditorState => {
  const content = editorState.getCurrentContent();
  const nextState = Modifier.replaceText(
    content,
    getAllSelection(content),
    response,
  );
  const newState = EditorState.push(
    editorState,
    nextState,
    'insert-characters',
  );
  return newState;
};

const processAction = async (
  editorState: EditorState,
  prompt: Prompt,
  editorStateHandler: (
    editorState: EditorState,
    response: string,
  ) => EditorState,
): Promise<EditorState> => {
  const content = editorState.getCurrentContent();
  const plainText = content.getPlainText();
  const response = await fetchAIResponse(plainText, prompt);
  return editorStateHandler(editorState, response);
};

function ToolbarDropdown({ onAction }: { onAction: (prompt: Prompt) => void }) {
  return (
    <div className="Draftail-AI-ButtonDropdown">
      {window.WAGTAIL_AI_PROMPTS.map((prompt) => (
        <button type="button" onMouseDown={() => onAction(prompt)}>
          <span>{prompt.label}</span> {prompt.description}
        </button>
      ))}
    </div>
  );
}

function ToolbarIcon() {
  return <Icon icon={<WandIcon />} />;
}

type ControlComponentPropsExtended = ControlComponentProps & {
  field: any;
};

function AIControl({
  getEditorState,
  onChange,
  field,
}: ControlComponentPropsExtended) {
  const editorState = getEditorState() as EditorState;
  const [isLoading, setIsLoading] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [error, setError] = useState(null);

  const handleClick = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const handleAction = async (prompt: Prompt) => {
    setError(null);
    setIsDropdownOpen(false);
    setIsLoading(true);
    try {
      if (prompt.method === 'append') {
        onChange(await processAction(editorState, prompt, handleAppend));
      } else {
        onChange(await processAction(editorState, prompt, handleReplace));
      }
    } catch (err) {
      setError(err.message);
    }
    setIsLoading(false);
  };

  return (
    <>
      <ToolbarButton
        name="AI Tools"
        icon={<ToolbarIcon />}
        onClick={handleClick}
      />
      {isDropdownOpen ? <ToolbarDropdown onAction={handleAction} /> : null}
      {error
        ? createPortal(
            <>
              <svg
                className="icon icon-warning w-field__errors-icon"
                aria-hidden="true"
              >
                <use href="#icon-warning"></use>
              </svg>
              <p className="error-message">{error}</p>
            </>,
            field.parentNode.previousElementSibling,
          )
        : null}
      {isLoading ? createPortal(<LoadingOverlay />, field.parentNode) : null}
    </>
  );
}

export default AIControl;