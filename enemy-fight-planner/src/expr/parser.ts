import { Lexer, Token, TokenType } from './lexer';

export type Expr =
  | { type: 'Number'; value: number }
  | { type: 'Var'; name: string }
  | { type: 'Binary'; op: string; left: Expr; right: Expr }
  | { type: 'Unary'; op: string; expr: Expr }
  | { type: 'Ternary'; cond: Expr; trueExpr: Expr; falseExpr: Expr }
  | { type: 'Call'; name: string; args: Expr[] };

export class Parser {
  private lexer: Lexer;
  private current!: Token;

  constructor(input: string) {
    this.lexer = new Lexer(input);
    this.next();
  }

  private next() {
    this.current = this.lexer.nextToken();
  }

  public parse(): Expr {
    const expr = this.parseTernary();
    if (this.current.type !== 'EOF') {
      throw new Error(`Unexpected token at end: ${this.current.value}`);
    }
    return expr;
  }

  private parseTernary(): Expr {
    let expr = this.parseOr();
    if (this.current.type === 'Question') {
      this.next();
      const trueExpr = this.parseTernary();
      if (this.current.type !== 'Colon') {
        throw new Error('Expected ":" in ternary expression');
      }
      this.next();
      const falseExpr = this.parseTernary();
      expr = { type: 'Ternary', cond: expr, trueExpr, falseExpr };
    }
    return expr;
  }

  private parseOr(): Expr {
    let expr = this.parseAnd();
    while (this.current.type === 'OrOr') {
      this.next();
      expr = { type: 'Binary', op: '||', left: expr, right: this.parseAnd() };
    }
    return expr;
  }

  private parseAnd(): Expr {
    let expr = this.parseEquality();
    while (this.current.type === 'AndAnd') {
      this.next();
      expr = { type: 'Binary', op: '&&', left: expr, right: this.parseEquality() };
    }
    return expr;
  }

  private parseEquality(): Expr {
    let expr = this.parseRelational();
    while (this.current.type === 'EqEq' || this.current.type === 'NotEq') {
      const op = this.current.value;
      this.next();
      expr = { type: 'Binary', op, left: expr, right: this.parseRelational() };
    }
    return expr;
  }

  private parseRelational(): Expr {
    let expr = this.parseAddSub();
    while (
      this.current.type === 'Lt' ||
      this.current.type === 'LtEq' ||
      this.current.type === 'Gt' ||
      this.current.type === 'GtEq'
    ) {
      const op = this.current.value;
      this.next();
      expr = { type: 'Binary', op, left: expr, right: this.parseAddSub() };
    }
    return expr;
  }

  private parseAddSub(): Expr {
    let expr = this.parseMulDiv();
    while (this.current.type === 'Plus' || this.current.type === 'Minus') {
      const op = this.current.value;
      this.next();
      expr = { type: 'Binary', op, left: expr, right: this.parseMulDiv() };
    }
    return expr;
  }

  private parseMulDiv(): Expr {
    let expr = this.parseUnary();
    while (this.current.type === 'Star' || this.current.type === 'Slash' || this.current.type === 'Percent') {
      const op = this.current.value;
      this.next();
      expr = { type: 'Binary', op, left: expr, right: this.parseUnary() };
    }
    return expr;
  }

  private parseUnary(): Expr {
    if (this.current.type === 'Minus' || this.current.type === 'Not') {
      const op = this.current.value;
      this.next();
      return { type: 'Unary', op, expr: this.parseUnary() };
    }
    return this.parsePrimary();
  }

  private parsePrimary(): Expr {
    if (this.current.type === 'Number') {
      const val = parseFloat(this.current.value);
      this.next();
      return { type: 'Number', value: val };
    }
    if (this.current.type === 'Ident') {
      const name = this.current.value;
      this.next();
      if (this.current.type === 'LParen') {
        this.next();
        const args: Expr[] = [];
        if (this.current.type !== 'RParen') {
          args.push(this.parseTernary());
          while (this.current.type === 'Comma') {
            this.next();
            args.push(this.parseTernary());
          }
        }
        if (this.current.type !== 'RParen') {
          throw new Error('Expected ")" after function arguments');
        }
        this.next();
        return { type: 'Call', name, args };
      }
      return { type: 'Var', name };
    }
    if (this.current.type === 'LParen') {
      this.next();
      const expr = this.parseTernary();
      if (this.current.type !== 'RParen') {
        throw new Error('Expected ")"');
      }
      this.next();
      return expr;
    }
    throw new Error(`Unexpected token: ${this.current.value}`);
  }
}
