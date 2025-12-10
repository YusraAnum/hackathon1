// Example test file to verify Jest setup
describe('Example Test Suite', () => {
  test('should pass a basic test', () => {
    expect(1 + 1).toBe(2);
  });

  test('should handle string operations', () => {
    const text = 'Hello, AI Textbook!';
    expect(text).toContain('AI Textbook');
  });
});