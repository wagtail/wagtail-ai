import React, { useState } from 'react';
import {
  EditorState,
  Modifier,
  SelectionState,
  ContentState,
  RichUtils,
} from 'draft-js';
import { ControlComponentProps, ToolbarButton, Icon } from 'draftail';
import Sparkle from 'react-sparkle';
import { createPortal } from 'react-dom';

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

type AIAction = 'completion' | 'correction';

const fetchAIResponse = async (
  text: string,
  action: AIAction,
): Promise<string> => {
  const res = await fetch(`/admin/ai/process?text=${text}&action=${action}`);
  const json = await res.json();
  return json.message;
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

const processAICompletion = async (
  editorState: EditorState,
): Promise<EditorState> => {
  const newEditorState = RichUtils.insertSoftNewline(editorState);
  const content = newEditorState.getCurrentContent();
  const plainText = content.getPlainText();
  const completion = await fetchAIResponse(plainText, 'completion');
  const nextState = Modifier.insertText(
    content,
    EditorState.moveSelectionToEnd(newEditorState).getSelection(),
    completion,
  );
  const newState = EditorState.push(
    newEditorState,
    nextState,
    'insert-characters',
  );
  return newState;
};

const processAICorrection = async (
  editorState: EditorState,
): Promise<EditorState> => {
  const content = editorState.getCurrentContent();
  const plainText = content.getPlainText();
  const completion = await fetchAIResponse(plainText, 'correction');
  const nextState = Modifier.replaceText(
    content,
    getAllSelection(content),
    completion,
  );
  const newState = EditorState.push(
    editorState,
    nextState,
    'insert-characters',
  );
  return newState;
};

function ToolbarDropdown({ onAction }: { onAction: (action: string) => void }) {
  return (
    <div className="Draftail-AI-ButtonDropdown">
      <button type="button" onMouseDown={() => onAction('completion')}>
        <span>AI Completion</span> Start writing and let AI finish for you.
      </button>
      <button type="button" onMouseDown={() => onAction('correction')}>
        <span>AI Correction</span> Let AI correct your spelling, grammar and
        punctuation.
      </button>
    </div>
  );
}

function ToolbarIcon() {
  return <Icon icon={<WandIcon />} />;
}

function AIControl({ getEditorState, onChange }: ControlComponentProps) {
  const editorState = getEditorState();
  const [isLoading, setIsLoading] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleClick = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const handleAction = async (action: AIAction) => {
    setIsDropdownOpen(false);
    setIsLoading(true);
    if (action === 'completion') {
      onChange(await processAICompletion(editorState));
    } else {
      onChange(await processAICorrection(editorState));
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
      {isLoading
        ? createPortal(
            <div className="Draftail-AI-Sparklebox">
              <Sparkle color="rgb(46,31,94)" fadeOutSpeed={5} />
            </div>,
            document.body,
          )
        : null}
    </>
  );
}

export default AIControl;
