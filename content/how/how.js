/* The /how-it-works/ page: the steps are all in the HTML; with JavaScript only the current one is shown, chosen by the address (#step-3).
   Without JavaScript every step is shown, one under the other, and the numbered links jump to them. Nothing leaves the page. */
(function () {
  /**
   * The element for a selector; the page cannot work without it.
   * @param {ParentNode} root - where to look.
   * @param {string} selector - the CSS selector.
   * @returns {Element} the first match.
   * @throws {Error} when nothing matches.
   */
  function one(root, selector) {
    var found = root.querySelector(selector);
    if (!found) { throw new Error('how: nothing matches ' + selector); }
    return found;
  }

  /**
   * The index of the step the address names; an address that names no step is an ordinary browser case and shows the first step.
   * @param {Element[]} steps - the step sections, in order.
   * @returns {number} the index to show.
   */
  function indexFromAddress(steps) {
    var found = steps.findIndex(function (step) { return step.id === location.hash.slice(1); });
    return found < 0 ? 0 : found;
  }

  /**
   * Mark one numbered link as the current step and the others as not.
   * @param {Element[]} tabs - the numbered links, in order.
   * @param {number} index - the current step.
   * @returns {void}
   */
  function markTabs(tabs, index) {
    tabs.forEach(function (tab, n) {
      tab.classList.toggle('is-current', n === index);
      if (n === index) { tab.setAttribute('aria-current', 'step'); } else { tab.removeAttribute('aria-current'); }
    });
  }

  /**
   * Show one step and hide the others; when the reader moved, bring the row of steps into view and put the focus on the step's heading.
   * @param {Element[]} steps - the step sections, in order.
   * @param {Element[]} tabs - the numbered links, in order.
   * @param {number} index - the step to show.
   * @param {boolean} moved - whether the reader just chose this step.
   * @returns {void}
   */
  function show(steps, tabs, index, moved) {
    steps.forEach(function (step, n) { step.hidden = n !== index; });
    markTabs(tabs, index);
    if (!moved) { return; }
    one(document, '.how__stepper').scrollIntoView();
    one(steps[index], 'h2').focus({ preventScroll: true });
  }

  var steps = Array.from(document.querySelectorAll('.how__step'));
  var tabs = Array.from(document.querySelectorAll('.how__tab'));
  if (steps.length !== tabs.length) { throw new Error('how: ' + steps.length + ' steps but ' + tabs.length + ' numbered links'); }
  document.documentElement.classList.add('how-live');
  show(steps, tabs, indexFromAddress(steps), location.hash !== '');
  window.addEventListener('hashchange', function () { show(steps, tabs, indexFromAddress(steps), true); });
})();
