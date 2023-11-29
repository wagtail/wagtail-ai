import { useEffect } from 'react';
import type { RefObject } from 'react';

/**
 * Attaches event listners to a handler method when a user
 * clicks outside of reference object
 */
export const useOutsideAlerter = (
  ref: RefObject<HTMLElement>,
  handler: () => void,
) => {
  useEffect(() => {
    /**
     * Alert if clicked on outside of element
     */
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        handler();
      }
    };
    // Bind the event listener
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      // Unbind the event listener on clean up
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [ref]);
};
