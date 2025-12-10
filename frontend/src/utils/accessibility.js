/**
 * Accessibility Utilities
 * This module provides utilities for WCAG compliance and accessibility features.
 */

/**
 * Focus management utility for keyboard navigation
 */
export class FocusManager {
  /**
   * Trap focus within an element (useful for modals)
   * @param {HTMLElement} element - The element to trap focus within
   */
  static trapFocus(element) {
    if (!element) return;

    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleKeyDown = (event) => {
      if (event.key === 'Tab') {
        if (event.shiftKey) {
          // Shift + Tab
          if (document.activeElement === firstElement) {
            lastElement.focus();
            event.preventDefault();
          }
        } else {
          // Tab
          if (document.activeElement === lastElement) {
            firstElement.focus();
            event.preventDefault();
          }
        }
      }
    };

    element.addEventListener('keydown', handleKeyDown);

    // Clean up function
    return () => {
      element.removeEventListener('keydown', handleKeyDown);
    };
  }

  /**
   * Focus the first focusable element in a container
   * @param {HTMLElement} container - The container element
   */
  static focusFirstElement(container) {
    if (!container) return;

    const firstFocusable = container.querySelector(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (firstFocusable) {
      firstFocusable.focus();
    }
  }
}

/**
 * ARIA live region utility for screen readers
 */
export class AriaLive {
  constructor() {
    this.container = null;
    this.createContainer();
  }

  createContainer() {
    // Create or reuse ARIA live region
    let existingContainer = document.querySelector('[data-aria-live-container]');

    if (existingContainer) {
      this.container = existingContainer;
    } else {
      this.container = document.createElement('div');
      this.container.setAttribute('data-aria-live-container', 'true');
      this.container.setAttribute('aria-live', 'polite');
      this.container.setAttribute('aria-atomic', 'true');
      this.container.style.position = 'absolute';
      this.container.style.left = '-10000px';
      this.container.style.top = 'auto';
      this.container.style.width = '1px';
      this.container.style.height = '1px';
      this.container.style.overflow = 'hidden';

      document.body.appendChild(this.container);
    }
  }

  /**
   * Announce a message to screen readers
   * @param {string} message - The message to announce
   * @param {'polite'|'assertive'} priority - The priority level
   */
  announce(message, priority = 'polite') {
    if (!this.container) return;

    this.container.textContent = message;
    this.container.setAttribute('aria-live', priority);

    // Reset after announcement
    setTimeout(() => {
      this.container.setAttribute('aria-live', 'polite');
      this.container.textContent = '';
    }, 1000);
  }
}

/**
 * Color contrast utility for WCAG compliance
 */
export class ColorContrast {
  /**
   * Calculate the contrast ratio between two colors
   * @param {string} backgroundColor - Background color in hex format
   * @param {string} textColor - Text color in hex format
   * @returns {number} Contrast ratio
   */
  static calculateContrastRatio(backgroundColor, textColor) {
    const bgLuminance = this.getRelativeLuminance(backgroundColor);
    const textLuminance = this.getRelativeLuminance(textColor);

    const lighter = Math.max(bgLuminance, textLuminance);
    const darker = Math.min(bgLuminance, textLuminance);

    return (lighter + 0.05) / (darker + 0.05);
  }

  /**
   * Get relative luminance of a color
   * @param {string} hexColor - Color in hex format
   * @returns {number} Relative luminance
   */
  static getRelativeLuminance(hexColor) {
    const rgb = this.hexToRgb(hexColor);
    const [r, g, b] = rgb.map(val => {
      val /= 255;
      return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
    });

    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }

  /**
   * Convert hex color to RGB
   * @param {string} hex - Hex color string
   * @returns {number[]} RGB values
   */
  static hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? [
      parseInt(result[1], 16),
      parseInt(result[2], 16),
      parseInt(result[3], 16)
    ] : [0, 0, 0]; // Default to black if invalid
  }

  /**
   * Check if contrast meets WCAG AA standards
   * @param {string} backgroundColor - Background color
   * @param {string} textColor - Text color
   * @param {boolean} largeText - Whether text is large (18pt+ or 14pt+ bold)
   * @returns {boolean} Whether contrast meets AA standards
   */
  static meetsWcagAa(backgroundColor, textColor, largeText = false) {
    const ratio = this.calculateContrastRatio(backgroundColor, textColor);
    return largeText ? ratio >= 3.0 : ratio >= 4.5;
  }

  /**
   * Check if contrast meets WCAG AAA standards
   * @param {string} backgroundColor - Background color
   * @param {string} textColor - Text color
   * @param {boolean} largeText - Whether text is large (18pt+ or 14pt+ bold)
   * @returns {boolean} Whether contrast meets AAA standards
   */
  static meetsWcagAaa(backgroundColor, textColor, largeText = false) {
    const ratio = this.calculateContrastRatio(backgroundColor, textColor);
    return largeText ? ratio >= 4.5 : ratio >= 7.0;
  }
}

/**
 * Accessibility utilities instance
 */
export const accessibilityUtils = {
  focusManager: new FocusManager(),
  ariaLive: new AriaLive(),
  colorContrast: ColorContrast
};

/**
 * Accessibility checker for components
 */
export const accessibilityCheck = {
  /**
   * Check if an element has proper ARIA labels
   * @param {HTMLElement} element - The element to check
   * @returns {boolean} Whether the element has proper ARIA labels
   */
  hasProperAriaLabels(element) {
    if (!element) return true; // Consider it valid if no element

    const role = element.getAttribute('role');
    const ariaLabel = element.getAttribute('aria-label');
    const ariaLabelledBy = element.getAttribute('aria-labelledby');
    const title = element.getAttribute('title');

    // For certain roles, we need ARIA labels
    const rolesRequiringLabels = ['button', 'link', 'menuitem', 'tab', 'checkbox', 'radio'];

    if (rolesRequiringLabels.includes(role) && !ariaLabel && !ariaLabelledBy && !title) {
      return false;
    }

    return true;
  },

  /**
   * Check if form elements have proper labels
   * @param {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement} element - The form element to check
   * @returns {boolean} Whether the element has proper labels
   */
  hasProperFormLabels(element) {
    if (!element) return true;

    // Check if element has an associated label
    const id = element.id;
    if (id) {
      const label = document.querySelector(`label[for="${id}"]`);
      if (label) return true;
    }

    // Check if element is inside a label
    let parent = element.parentElement;
    while (parent) {
      if (parent.tagName.toLowerCase() === 'label') {
        return true;
      }
      parent = parent.parentElement;
    }

    // Check if element has aria-label or aria-labelledby
    const ariaLabel = element.getAttribute('aria-label');
    const ariaLabelledBy = element.getAttribute('aria-labelledby');

    return !!(ariaLabel || ariaLabelledBy);
  }
};

export default accessibilityUtils;