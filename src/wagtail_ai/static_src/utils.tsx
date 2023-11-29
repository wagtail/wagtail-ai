import {
  EditorState,
  Modifier,
  SelectionState,
  ContentState,
  RichUtils,
} from 'draft-js';

import type { Prompt } from './custom';

class APIRequestError extends Error {}

const fetchAIResponse = async (
  text: string,
  prompt: Prompt,
  signal: AbortSignal,
): Promise<string> => {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('prompt', prompt.id);
  try {
    const res = await fetch(window.WAGTAIL_AI_PROCESS_URL, {
      method: 'POST',
      body: formData,
      signal: signal,
    });
    const json = await res.json();
    if (res.ok) {
      return json.message;
    } else {
      throw new APIRequestError(json.error);
    }
  } catch (err) {
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
