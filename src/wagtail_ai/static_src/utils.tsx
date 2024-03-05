import {
  EditorState,
  Modifier,
  SelectionState,
  ContentState,
  RichUtils,
} from 'draft-js';

import type { Prompt } from './custom';
import { fetchAIResponse } from './api';

const getAllSelection = (content: ContentState): SelectionState => {
  const blockMap = content.getBlockMap();
  return new SelectionState({
    anchorKey: blockMap.first().getKey(),
    anchorOffset: 0,
    focusKey: blockMap.last().getKey(),
    focusOffset: blockMap.last().getLength(),
  });
};

export const handleAppend = (
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

export const handleReplace = (
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

export const processAction = async (
  editorState: EditorState,
  prompt: Prompt,
  editorStateHandler: (
    editorState: EditorState,
    response: string,
  ) => EditorState,
  abortController: AbortController, // Pass the AbortController instance
): Promise<EditorState> => {
  const content = editorState.getCurrentContent();
  const plainText = content.getPlainText();
  const response = await fetchAIResponse(
    plainText,
    prompt,
    abortController.signal,
  );
  return editorStateHandler(editorState, response);
};
