import { describe, expect, it } from "vitest";

describe("Trinity Studio web", () => {
  it("loads test runner", () => {
    expect(import.meta.env).toBeDefined();
  });
});
