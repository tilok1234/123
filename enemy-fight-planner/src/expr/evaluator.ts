import { Expr, Parser } from './parser';

export type Context = Record<string, number>;

export class Evaluator {
  private builtins: Record<string, (...args: number[]) => number> = {
    min: Math.min,
    max: Math.max,
    clamp: (x, a, b) => Math.max(a, Math.min(x, b)),
    lerp: (a, b, t) => a + (b - a) * t,
    abs: Math.abs,
    floor: Math.floor,
    ceil: Math.ceil,
    round: Math.round,
    sin: Math.sin,
    cos: Math.cos,
    tan: Math.tan,
    deg2rad: (d) => d * (Math.PI / 180),
    rad2deg: (r) => r * (180 / Math.PI),
  };

  public evaluateString(input: string, context: Context): number {
    const parser = new Parser(input);
    const ast = parser.parse();
    return this.evaluate(ast, context);
  }

  public evaluate(expr: Expr, context: Context): number {
    switch (expr.type) {
      case 'Number':
        return expr.value;
      case 'Var':
        if (!(expr.name in context)) {
          throw new Error(`Undefined variable: ${expr.name}`);
        }
        return context[expr.name];
      case 'Unary': {
        const val = this.evaluate(expr.expr, context);
        if (expr.op === '-') return -val;
        if (expr.op === '!') return val ? 0 : 1;
        throw new Error(`Unknown unary operator: ${expr.op}`);
      }
      case 'Binary': {
        const left = this.evaluate(expr.left, context);
        // Short-circuiting for logical operators
        if (expr.op === '&&') return left ? this.evaluate(expr.right, context) : 0;
        if (expr.op === '||') return left ? left : this.evaluate(expr.right, context);

        const right = this.evaluate(expr.right, context);
        switch (expr.op) {
          case '+': return left + right;
          case '-': return left - right;
          case '*': return left * right;
          case '/': return left / right;
          case '%': return left % right;
          case '==': return left === right ? 1 : 0;
          case '!=': return left !== right ? 1 : 0;
          case '<': return left < right ? 1 : 0;
          case '<=': return left <= right ? 1 : 0;
          case '>': return left > right ? 1 : 0;
          case '>=': return left >= right ? 1 : 0;
          default: throw new Error(`Unknown binary operator: ${expr.op}`);
        }
      }
      case 'Ternary': {
        const cond = this.evaluate(expr.cond, context);
        return cond ? this.evaluate(expr.trueExpr, context) : this.evaluate(expr.falseExpr, context);
      }
      case 'Call': {
        if (!(expr.name in this.builtins)) {
          throw new Error(`Unknown function: ${expr.name}`);
        }
        const args = expr.args.map(arg => this.evaluate(arg, context));
        return this.builtins[expr.name](...args);
      }
    }
  }
}

export function evaluate(expression: string | number, context: Context): number {
  if (typeof expression === 'number') return expression;
  return new Evaluator().evaluateString(expression, context);
}
