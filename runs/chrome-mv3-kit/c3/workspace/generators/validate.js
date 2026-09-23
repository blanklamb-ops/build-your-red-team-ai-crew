"use strict";
const fs = require("fs");
const path = require("path");
const { parseYaml } = require("./yaml");

function validateSchema(value, schema, location = "$") {
  const errors = [];
  const types = Array.isArray(schema.type) ? schema.type : schema.type ? [schema.type] : [];
  const actual = value === null ? "null" : Array.isArray(value) ? "array" : typeof value;
  if (types.length && !types.includes(actual)) return [`${location}: expected ${types.join(" or ")}, got ${actual}`];
  if (Object.prototype.hasOwnProperty.call(schema, "const") && value !== schema.const) errors.push(`${location}: must equal ${JSON.stringify(schema.const)}`);
  if (schema.enum && !schema.enum.includes(value)) errors.push(`${location}: must be one of ${schema.enum.join(", ")}`);
  if (typeof value === "string" && schema.minLength && value.length < schema.minLength) errors.push(`${location}: string is too short`);
  if (Array.isArray(value)) {
    if (schema.minItems && value.length < schema.minItems) errors.push(`${location}: requires at least ${schema.minItems} item(s)`);
    if (schema.items) value.forEach((item, index) => errors.push(...validateSchema(item, schema.items, `${location}[${index}]`)));
  } else if (value && typeof value === "object") {
    for (const key of schema.required || []) if (!Object.prototype.hasOwnProperty.call(value, key)) errors.push(`${location}: missing required property ${key}`);
    if (schema.additionalProperties === false && schema.properties) {
      for (const key of Object.keys(value)) if (!Object.prototype.hasOwnProperty.call(schema.properties, key)) errors.push(`${location}: unexpected property ${key}`);
    }
    for (const [key, childSchema] of Object.entries(schema.properties || {})) {
      if (Object.prototype.hasOwnProperty.call(value, key)) errors.push(...validateSchema(value[key], childSchema, `${location}.${key}`));
    }
  }
  return errors;
}

function loadSchema() {
  return JSON.parse(fs.readFileSync(path.join(__dirname, "../schemas/phishlet-schema-2.3.0.json"), "utf8"));
}

function validatePhishlet(value, schema = loadSchema()) {
  const errors = validateSchema(value, schema);
  function walk(node, location = "$") {
    if (typeof node === "string" && node.includes("{{PLACEHOLDER}}")) errors.push(`${location}: placeholder token is forbidden`);
    else if (Array.isArray(node)) node.forEach((child, i) => walk(child, `${location}[${i}]`));
    else if (node && typeof node === "object") Object.entries(node).forEach(([key, child]) => walk(child, `${location}.${key}`));
  }
  walk(value);
  return { valid: errors.length === 0, errors };
}

function validateYaml(text) {
  let value;
  try { value = parseYaml(text); } catch (error) { return { valid: false, errors: [error.message] }; }
  return Object.assign({ value }, validatePhishlet(value));
}

module.exports = { validateSchema, validatePhishlet, validateYaml, loadSchema };
