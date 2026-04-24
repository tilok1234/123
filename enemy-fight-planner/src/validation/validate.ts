import Ajv from 'ajv';
import patternSchema from '../schema/pattern.schema.json';
import sequenceSchema from '../schema/sequence.schema.json';
import projectileSchema from '../schema/projectile.schema.json';
import movementSchema from '../schema/movement.schema.json';

const ajv = new Ajv({
    schemas: [patternSchema, sequenceSchema, projectileSchema, movementSchema],
    allowUnionTypes: true
});

export function validatePattern(data: unknown): boolean {
  return !!ajv.validate('pattern.schema.json', data);
}

export function validateSequence(data: unknown): boolean {
  return !!ajv.validate('sequence.schema.json', data);
}

export function validateProjectile(data: unknown): boolean {
  return !!ajv.validate('projectile.schema.json', data);
}

export function getErrors() {
    return ajv.errors;
}
