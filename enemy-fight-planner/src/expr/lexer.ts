export type TokenType =
  | 'Number'
  | 'Ident'
  | 'Plus'
  | 'Minus'
  | 'Star'
  | 'Slash'
  | 'Percent'
  | 'LParen'
  | 'RParen'
  | 'Comma'
  | 'Question'
  | 'Colon'
  | 'EqEq'
  | 'NotEq'
  | 'Lt'
  | 'LtEq'
  | 'Gt'
  | 'GtEq'
  | 'AndAnd'
  | 'OrOr'
  | 'Not'
  | 'EOF';

export interface Token {
  type: TokenType;
  value: string;
}

export class Lexer {
  private pos = 0;
  constructor(private input: string) {}

  public nextToken(): Token {
    this.skipWhitespace();

    if (this.pos >= this.input.length) {
      return { type: 'EOF', value: '' };
    }

    const char = this.input[this.pos];

    if (char === '+') return this.advance('Plus');
    if (char === '-') return this.advance('Minus');
    if (char === '*') return this.advance('Star');
    if (char === '/') return this.advance('Slash');
    if (char === '%') return this.advance('Percent');
    if (char === '(') return this.advance('LParen');
    if (char === ')') return this.advance('RParen');
    if (char === ',') return this.advance('Comma');
    if (char === '?') return this.advance('Question');
    if (char === ':') return this.advance('Colon');

    if (char === '=') {
      if (this.peek() === '=') {
        this.pos += 2;
        return { type: 'EqEq', value: '==' };
      }
    }
    if (char === '!') {
      if (this.peek() === '=') {
        this.pos += 2;
        return { type: 'NotEq', value: '!=' };
      }
      return this.advance('Not');
    }
    if (char === '<') {
      if (this.peek() === '=') {
        this.pos += 2;
        return { type: 'LtEq', value: '<=' };
      }
      return this.advance('Lt');
    }
    if (char === '>') {
      if (this.peek() === '=') {
        this.pos += 2;
        return { type: 'GtEq', value: '>=' };
      }
      return this.advance('Gt');
    }
    if (char === '&' && this.peek() === '&') {
      this.pos += 2;
      return { type: 'AndAnd', value: '&&' };
    }
    if (char === '|' && this.peek() === '|') {
      this.pos += 2;
      return { type: 'OrOr', value: '||' };
    }

    if (this.isDigit(char) || char === '.') {
      return this.readNumber();
    }

    if (this.isAlpha(char) || char === '$') {
      return this.readIdent();
    }

    throw new Error(`Unexpected character: ${char} at pos ${this.pos}`);
  }

  private advance(type: TokenType): Token {
    const value = this.input[this.pos];
    this.pos++;
    return { type, value };
  }

  private peek(): string {
    return this.pos + 1 < this.input.length ? this.input[this.pos + 1] : '';
  }

  private skipWhitespace() {
    while (this.pos < this.input.length && /\s/.test(this.input[this.pos])) {
      this.pos++;
    }
  }

  private isDigit(char: string): boolean {
    return /[0-9]/.test(char);
  }

  private isAlpha(char: string): boolean {
    return /[a-zA-Z_]/.test(char);
  }

  private readNumber(): Token {
    let value = '';
    while (this.pos < this.input.length && (this.isDigit(this.input[this.pos]) || this.input[this.pos] === '.')) {
      value += this.input[this.pos];
      this.pos++;
    }
    return { type: 'Number', value };
  }

  private readIdent(): Token {
    let value = '';
    while (this.pos < this.input.length && (this.isAlpha(this.input[this.pos]) || this.isDigit(this.input[this.pos]) || this.input[this.pos] === '$')) {
      value += this.input[this.pos];
      this.pos++;
    }
    return { type: 'Ident', value };
  }
}
