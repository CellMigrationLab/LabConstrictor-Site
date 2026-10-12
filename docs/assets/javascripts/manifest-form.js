/* The form on /submit/ that writes labconstrictor-app.yaml in the browser. Nothing is sent anywhere: the form builds the manifest,
   checks it against the published schema (the same file the App Centre checks), shows the YAML and offers it as a download.
   The checks are read from the schema itself, so the form cannot ask for something the App Centre would refuse, or the reverse. */
(function () {
  "use strict";

  /** The order of the keys in the written file: the order of the example on the page. */
  const ORDER = ["schema", "name", "summary", "description", "kind", "hosts", "distribution", "license", "status", "authors", "inputs", "outputs",
    "limitations", "quickstart", "categories", "doi", "homepage", "docs_url", "icon", "screenshots"];

  /**
   * The element for a selector; the form cannot work without it.
   * @param {ParentNode} root - where to look.
   * @param {string} selector - the CSS selector.
   * @returns {HTMLElement} the first match.
   * @throws {Error} when nothing matches.
   */
  function one(root, selector) {
    const found = root.querySelector(selector);
    if (!found) throw new Error("manifest form: nothing matches " + selector);
    return found;
  }

  /**
   * The non-empty lines of a text area, trimmed.
   * @param {string} text - the text.
   * @returns {string[]} the lines.
   */
  function lines(text) {
    return text.split("\n").map((l) => l.trim()).filter((l) => l !== "");
  }

  /**
   * A line "first | second" split at its first bar, both parts trimmed (the second is "" when there is no bar).
   * @param {string} line - the line.
   * @returns {string[]} the two parts.
   */
  function pair(line) {
    const at = line.indexOf("|");
    return at < 0 ? [line.trim(), ""] : [line.slice(0, at).trim(), line.slice(at + 1).trim()];
  }

  /**
   * The manifest the form describes: only the fields that were filled in (an empty field is left out, never written empty).
   * @param {HTMLFormElement} form - the form.
   * @returns {Object} the manifest.
   */
  function manifestOf(form) {
    const v = (name) => form.elements[name].value.trim();
    const m = { schema: 1, name: v("name"), summary: v("summary"), kind: v("kind") };
    if (v("description")) m.description = form.elements.description.value.trim().replace(/\r\n/g, "\n");
    const hosts = Array.from(form.querySelectorAll('input[name="hosts"]:checked')).map((b) => b.value);
    if (hosts.length) m.hosts = hosts;
    const dist = {};
    if (form.elements.installer.checked) dist.installer = true;
    const colab = lines(v("colab")).map(pair).map(([label, url]) => ({ label: label, url: url }));
    if (colab.length) dist.colab = colab;
    if (v("pip")) dist.pip = v("pip");
    m.distribution = dist;
    if (v("license")) m.license = v("license");
    if (v("status")) m.status = v("status");
    const authors = lines(v("authors")).map(pair).map(([name, orcid]) => (orcid ? { name: name, orcid: orcid } : { name: name }));
    if (authors.length) m.authors = authors;
    ["inputs", "outputs", "limitations", "quickstart"].forEach((key) => { const l = lines(v(key)); if (l.length) m[key] = l; });
    const categories = v("categories").split(",").map((c) => c.trim()).filter((c) => c !== "");
    if (categories.length) m.categories = categories;
    ["doi", "homepage", "docs_url", "icon"].forEach((key) => { if (v(key)) m[key] = v(key); });
    const shots = lines(v("screenshots")).map(pair).map(([path, caption]) => ({ path: path, caption: caption }));
    if (shots.length) m.screenshots = shots;
    return m;
  }

  /**
   * Follow a local "$ref" ("#/$defs/name") to the part of the schema it names; any other node is returned as it is.
   * @param {Object} root - the whole schema.
   * @param {Object} node - a schema node.
   * @returns {Object} the node to use.
   */
  function resolve(root, node) {
    if (!node.$ref) return node;
    const target = node.$ref.replace(/^#\//, "").split("/").reduce((at, key) => at[key], root);
    const rest = Object.assign({}, node);
    delete rest.$ref;
    return Object.assign({}, target, rest);
  }

  /**
   * Check a value against a schema node. Covers what the manifest schema uses: type, const, enum, minLength, maxLength, pattern,
   * minItems, maxItems, uniqueItems, items, required, properties, additionalProperties, anyOf of required keys, dependentRequired.
   * @param {Object} root - the whole schema (for $ref).
   * @param {Object} node - the schema node for this value.
   * @param {*} value - the value.
   * @param {string} path - where the value is ("name", "distribution.colab.1.url").
   * @param {Array<{path: string, message: string}>} out - the problems found, added to.
   * @returns {void}
   */
  function check(root, node, value, path, out) {
    const s = resolve(root, node);
    const say = (message) => out.push({ path: path, message: message });
    if ("const" in s && value !== s.const) say("must be " + JSON.stringify(s.const));
    if (s.enum && !s.enum.includes(value)) say("must be one of: " + s.enum.join(", "));
    if (s.type === "string" || typeof value === "string") {
      if (typeof value !== "string") { say("must be text"); return; }
      if (s.minLength !== undefined && value.length < s.minLength) say("needs at least " + s.minLength + " characters (now " + value.length + ")");
      if (s.maxLength !== undefined && value.length > s.maxLength) say("may have at most " + s.maxLength + " characters (now " + value.length + ")");
      if (s.pattern && !new RegExp(s.pattern).test(value)) say("is not in the expected form");
    }
    if (s.type === "array") {
      if (!Array.isArray(value)) { say("must be a list"); return; }
      if (s.minItems !== undefined && value.length < s.minItems) say("needs at least " + s.minItems + " entries");
      if (s.maxItems !== undefined && value.length > s.maxItems) say("may have at most " + s.maxItems + " entries");
      if (s.uniqueItems && new Set(value.map((x) => JSON.stringify(x))).size !== value.length) say("has the same entry twice");
      if (s.items) value.forEach((item, i) => check(root, s.items, item, path + "." + (i + 1), out));
    }
    if (s.type === "object" || s.properties) {
      if (typeof value !== "object" || value === null || Array.isArray(value)) { say("must be a group of fields"); return; }
      (s.required || []).forEach((key) => { if (!(key in value)) out.push({ path: path ? path + "." + key : key, message: "is required" }); });
      if (s.anyOf && !s.anyOf.some((alt) => (alt.required || []).every((key) => key in value))) say("needs at least one of: " + s.anyOf.map((alt) => alt.required.join(" + ")).join(", "));
      Object.entries(s.dependentRequired || {}).forEach(([key, needs]) => { if (key in value) needs.forEach((n) => { if (!(n in value)) say(key + " needs " + n); }); });
      Object.keys(value).forEach((key) => {
        const where = path ? path + "." + key : key;
        if (s.properties && s.properties[key]) check(root, s.properties[key], value[key], where, out);
        else if (s.additionalProperties === false) out.push({ path: where, message: "is not a field of the manifest" });
      });
    }
  }

  /**
   * A value written as YAML at the given indentation. Text is always quoted (a JSON string is a valid YAML string), so no value can be
   * read back as something else (a number, a date, a list).
   * @param {*} value - the value.
   * @param {string} pad - the indentation of its lines.
   * @returns {string} the YAML, starting with a space or a new line.
   */
  function yamlValue(value, pad) {
    if (Array.isArray(value)) {
      return value.map((item) => {
        if (typeof item === "object") {
          const body = Object.keys(item).map((k, i) => (i === 0 ? "" : pad + "  ") + k + ":" + yamlValue(item[k], pad + "    ")).join("\n");
          return "\n" + pad + "- " + body;
        }
        return "\n" + pad + "- " + JSON.stringify(item);
      }).join("");
    }
    if (typeof value === "object") return Object.keys(value).map((k) => "\n" + pad + k + ":" + yamlValue(value[k], pad + "  ")).join("");
    if (typeof value === "string" && value.includes("\n")) return " |-\n" + value.split("\n").map((l) => (l ? pad + l : "")).join("\n");
    return " " + (typeof value === "string" ? JSON.stringify(value) : String(value));
  }

  /**
   * The whole file: the schema line for editors, then the fields in the order of the example.
   * @param {Object} manifest - the manifest.
   * @param {string} schemaUrl - the published address of the schema.
   * @returns {string} the file's text.
   */
  function yamlOf(manifest, schemaUrl) {
    const keys = ORDER.filter((k) => k in manifest);
    return "# yaml-language-server: $schema=" + schemaUrl + "\n" + keys.map((k) => k + ":" + yamlValue(manifest[k], "  ")).join("\n") + "\n";
  }

  /**
   * The form field a problem belongs to: the first part of its path, with the routes of distribution mapped to their own fields.
   * @param {string} path - the problem's path.
   * @returns {string} the field's name.
   */
  function fieldOf(path) {
    const parts = path.split(".");
    return parts[0] === "distribution" && parts[1] ? (parts[1] === "installer" ? "installer" : parts[1]) : parts[0];
  }

  /**
   * Show the YAML, the problems (each beside its field and in the list) and whether the file can be downloaded.
   * @param {HTMLElement} root - the form's section.
   * @param {Object} schema - the schema.
   * @returns {void}
   */
  function refresh(root, schema) {
    const form = /** @type {HTMLFormElement} */ (one(root, "form"));
    const manifest = manifestOf(form);
    const problems = [];
    check(schema, schema, manifest, "", problems);
    const text = yamlOf(manifest, schema.$id);
    one(root, "[data-mf-yaml]").textContent = text;
    root.querySelectorAll("[data-mf-error]").forEach((el) => { el.textContent = ""; });
    form.querySelectorAll("[aria-invalid]").forEach((el) => el.removeAttribute("aria-invalid"));
    problems.forEach((p) => {
      const field = fieldOf(p.path);
      const note = root.querySelector('[data-mf-error="' + field + '"]');
      if (note) note.textContent = (note.textContent ? note.textContent + " " : "") + p.path + " " + p.message + ".";
      const control = form.elements[field];
      if (control && control.setAttribute) control.setAttribute("aria-invalid", "true");
    });
    const status = one(root, "[data-mf-status]");
    status.textContent = problems.length ? problems.length + (problems.length === 1 ? " field needs" : " fields need") + " attention before the file is ready."
      : "The file is ready: it passes the same checks as the App Centre.";
    status.classList.toggle("is-ok", !problems.length);
    const download = /** @type {HTMLButtonElement} */ (one(root, "[data-mf-download]"));
    download.disabled = problems.length > 0;
    download.dataset.text = text;
  }

  /**
   * Start the form once the schema is read: fill the choices from the schema, then redraw on every change.
   * @param {HTMLElement} root - the form's section.
   * @param {Object} schema - the schema.
   * @returns {void}
   */
  function start(root, schema) {
    const kinds = one(root, 'select[name="kind"]');
    schema.properties.kind.enum.forEach((k) => kinds.append(new Option(k, k)));
    const statuses = one(root, 'select[name="status"]');
    schema.properties.status.enum.forEach((k) => statuses.append(new Option(k, k)));
    const hosts = one(root, "[data-mf-hosts]");
    schema.properties.hosts.items.enum.forEach((h) => {
      const label = document.createElement("label");
      const box = document.createElement("input");
      Object.assign(box, { type: "checkbox", name: "hosts", value: h, checked: h === "notebook" });
      label.append(box, " " + h);
      hosts.append(label);
    });
    const form = one(root, "form");
    form.addEventListener("input", () => refresh(root, schema));
    form.addEventListener("submit", (e) => e.preventDefault());
    one(root, "[data-mf-download]").addEventListener("click", (e) => {
      const text = /** @type {HTMLElement} */ (e.currentTarget).dataset.text || "";
      const link = document.createElement("a");
      link.href = URL.createObjectURL(new Blob([text], { type: "text/yaml" }));
      link.download = "labconstrictor-app.yaml";
      link.click();
      setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    });
    one(root, "[data-mf-copy]").addEventListener("click", (e) => {
      const button = /** @type {HTMLButtonElement} */ (e.currentTarget);
      navigator.clipboard.writeText(one(root, "[data-mf-yaml]").textContent || "").then(() => { button.textContent = "Copied"; setTimeout(() => { button.textContent = "Copy"; }, 1500); });
    });
    root.hidden = false;
    one(document, "[data-mf-fallback]").hidden = true;
    refresh(root, schema);
  }

  const root = document.querySelector("[data-manifest-form]");
  if (!root) return;
  fetch(root.dataset.schema).then((r) => {
    if (!r.ok) throw new Error("manifest form: the schema answered " + r.status);
    return r.json();
  }).then((schema) => start(root, schema));
})();
