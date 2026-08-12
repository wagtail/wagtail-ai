/** @type {import('stylelint').Config} */
export default {
  extends: ['@wagtail/stylelint-config-wagtail'],
  rules: {
    // TODO: Address these as part of separate CSS refactoring work.
    'scale-unlimited/declaration-strict-value': null,
    'selector-attribute-name-disallowed-list': null,
    'scss/selector-class-pattern': null,
    'selector-max-id': null,
    'selector-max-specificity': null,
    'declaration-property-value-disallowed-list': null,
    'declaration-property-value-allowed-list': null,
    'property-disallowed-list': null,
  },
};
