"use strict";

function scalar(value) {
  if (value === null) return "null";
  if (typeof value === "boolean" || typeof value === "number") return String(value);
  return JSON.stringify(String(value));
}

function serializeYaml(value, headerComments = []) {
  const lines = headerComments.map((line) => `# ${line}`);
  function emit(node, indent, prefix) {
    const pad = " ".repeat(indent);
    if (Array.isArray(node)) {
      if (!node.length) { lines.push(`${pad}${prefix || ""}[]`); return; }
      if (prefix) lines.push(`${pad}${prefix}`);
      for (const item of node) {
        if (item && typeof item === "object" && !Array.isArray(item)) {
          const entries = Object.entries(item);
          const [firstKey, firstValue] = entries[0];
          if (firstValue && typeof firstValue === "object") {
            lines.push(`${" ".repeat(indent + (prefix ? 2 : 0))}- ${firstKey}:`);
            emit(firstValue, indent + (prefix ? 6 : 4), "");
          } else {
            lines.push(`${" ".repeat(indent + (prefix ? 2 : 0))}- ${firstKey}: ${scalar(firstValue)}`);
          }
          for (const [key, child] of entries.slice(1)) {
            const childIndent = indent + (prefix ? 4 : 2);
            if (child && typeof child === "object") emit(child, childIndent, `${key}:`);
            else lines.push(`${" ".repeat(childIndent)}${key}: ${scalar(child)}`);
          }
        } else lines.push(`${" ".repeat(indent + (prefix ? 2 : 0))}- ${scalar(item)}`);
      }
      return;
    }
    if (node && typeof node === "object") {
      if (prefix) lines.push(`${pad}${prefix}`);
      const base = indent + (prefix ? 2 : 0);
      for (const [key, child] of Object.entries(node)) {
        if (child && typeof child === "object") emit(child, base, `${key}:`);
        else lines.push(`${" ".repeat(base)}${key}: ${scalar(child)}`);
      }
    }
  }
  emit(value, 0, "");
  return `${lines.join("\n")}\n`;
}

function parseScalar(text) {
  const value = text.trim();
  if (value === "[]") return [];
  if (value === "{}") return {};
  if (value === "null") return null;
  if (value === "true") return true;
  if (value === "false") return false;
  if (/^-?\d+(\.\d+)?$/.test(value)) return Number(value);
  if (value.startsWith('"')) {
    try { return JSON.parse(value); } catch (_) { throw new Error(`Invalid quoted scalar: ${value}`); }
  }
  if (value.startsWith("'")) {
    if (!value.endsWith("'")) throw new Error(`Invalid quoted scalar: ${value}`);
    return value.slice(1, -1).replace(/''/g, "'");
  }
  if (!value || /[\[\]{}]/.test(value)) throw new Error(`Unsupported or malformed scalar: ${value}`);
  return value;
}

function parseYaml(text) {
  if (typeof text !== "string") throw new Error("YAML text is required");
  const rows = text.split(/\r?\n/).map((raw, index) => ({
    raw, index: index + 1, indent: raw.match(/^ */)[0].length, text: raw.trim()
  })).filter((row) => row.text && !row.text.startsWith("#"));
  for (const row of rows) {
    if (/\t/.test(row.raw.slice(0, row.raw.length - row.text.length))) throw new Error(`Tabs are not valid indentation at line ${row.index}`);
    if (row.indent % 2) throw new Error(`Indentation must use two-space levels at line ${row.index}`);
  }
  let cursor = 0;
  function block(indent) {
    if (cursor >= rows.length || rows[cursor].indent < indent) throw new Error("Expected nested YAML block");
    const sequence = rows[cursor].indent === indent && rows[cursor].text.startsWith("- ");
    const output = sequence ? [] : {};
    while (cursor < rows.length && rows[cursor].indent === indent) {
      const row = rows[cursor];
      if (sequence) {
        if (!row.text.startsWith("- ")) throw new Error(`Mixed mapping and sequence at line ${row.index}`);
        const rest = row.text.slice(2);
        cursor++;
        const mapMatch = rest.match(/^([^:]+):(?:\s+(.*))?$/);
        if (!mapMatch) { output.push(parseScalar(rest)); continue; }
        const item = {};
        item[mapMatch[1]] = mapMatch[2] === undefined ? block(indent + 4) : parseScalar(mapMatch[2]);
        while (cursor < rows.length && rows[cursor].indent === indent + 2 && !rows[cursor].text.startsWith("- ")) {
          const child = rows[cursor];
          const match = child.text.match(/^([^:]+):(?:\s+(.*))?$/);
          if (!match) throw new Error(`Malformed mapping at line ${child.index}`);
          cursor++;
          item[match[1]] = match[2] === undefined ? block(indent + 4) : parseScalar(match[2]);
        }
        output.push(item);
      } else {
        if (row.text.startsWith("- ")) throw new Error(`Mixed mapping and sequence at line ${row.index}`);
        const match = row.text.match(/^([^:]+):(?:\s+(.*))?$/);
        if (!match) throw new Error(`Malformed mapping at line ${row.index}`);
        cursor++;
        output[match[1]] = match[2] === undefined ? block(indent + 2) : parseScalar(match[2]);
      }
    }
    return output;
  }
  if (!rows.length) throw new Error("YAML document is empty");
  const result = block(rows[0].indent);
  if (cursor !== rows.length) throw new Error(`Unexpected indentation at line ${rows[cursor].index}`);
  return result;
}

module.exports = { serializeYaml, parseYaml };
