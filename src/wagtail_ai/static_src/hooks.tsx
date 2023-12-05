import { useEffect, useRef } from 'react';
import type { RefObject } from 'react';

/**
 * Attaches event listners to a handler method when a user
 * clicks outside of the reference object
 */
export const useOutsideAlerter = (
  ref: RefObject<HTMLElement>,
  handler: () => void,
) => {
  const handleClickOutside = (event: MouseEvent) => {
    if (ref.current && !ref.current.contains(event.target as Node)) {
      handler();
    }
  };

  const handleClickOutsideRef = useRef(handleClickOutside);

  useEffect(() => {
    // Bind the event listener
    document.addEventListener('mousedown', handleClickOutsideRef.current);

    return () => {
      // Unbind the event listener on cleanup
      document.removeEventListener('mousedown', handleClickOutsideRef.current);
    };
  }, [handleClickOutsideRef]);
};
