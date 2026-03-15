import { fetchWithRetry } from "@/lib/api";

// Store the original fetch
const originalFetch = global.fetch;

// Helper to create a mock Response
function createMockResponse(body: string, status: number): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? "OK" : "Error",
    json: () => Promise.resolve(JSON.parse(body)),
    text: () => Promise.resolve(body),
    headers: new Headers(),
    redirected: false,
    type: "basic",
    url: "",
    clone: function() { return this; },
    body: null,
    bodyUsed: false,
    arrayBuffer: () => Promise.resolve(new ArrayBuffer(0)),
    blob: () => Promise.resolve(new Blob()),
    formData: () => Promise.resolve(new FormData()),
    bytes: () => Promise.resolve(new Uint8Array()),
  } as Response;
}

describe("fetchWithRetry", () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
    global.fetch = originalFetch;
  });

  it("should return response on successful fetch", async () => {
    const mockResponse = createMockResponse(JSON.stringify({ success: true }), 200);
    global.fetch = jest.fn().mockResolvedValue(mockResponse);

    const promise = fetchWithRetry("http://test.com/api");
    jest.runAllTimers();
    const result = await promise;

    expect(result).toBe(mockResponse);
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it("should retry on retryable status codes", async () => {
    const failResponse = createMockResponse("Server Error", 503);
    const successResponse = createMockResponse(JSON.stringify({ success: true }), 200);

    global.fetch = jest
      .fn()
      .mockResolvedValueOnce(failResponse)
      .mockResolvedValueOnce(successResponse);

    const promise = fetchWithRetry("http://test.com/api");

    // Advance past the first retry delay
    await jest.advanceTimersByTimeAsync(1000);
    await jest.advanceTimersByTimeAsync(500);

    const result = await promise;

    expect(result).toBe(successResponse);
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  it("should not retry on non-retryable status codes", async () => {
    const notFoundResponse = createMockResponse("Not Found", 404);
    global.fetch = jest.fn().mockResolvedValue(notFoundResponse);

    const promise = fetchWithRetry("http://test.com/api");
    jest.runAllTimers();
    const result = await promise;

    expect(result).toBe(notFoundResponse);
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it("should retry on network errors", async () => {
    const successResponse = createMockResponse(JSON.stringify({ success: true }), 200);

    global.fetch = jest
      .fn()
      .mockRejectedValueOnce(new Error("Failed to fetch"))
      .mockResolvedValueOnce(successResponse);

    const promise = fetchWithRetry("http://test.com/api");

    // Advance past the first retry delay
    await jest.advanceTimersByTimeAsync(1500);

    const result = await promise;

    expect(result).toBe(successResponse);
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  it("should throw after max retries exceeded", async () => {
    jest.useRealTimers(); // Use real timers for this test
    
    global.fetch = jest.fn().mockRejectedValue(new Error("Failed to fetch"));

    await expect(
      fetchWithRetry("http://test.com/api", {
        retryConfig: { 
          maxRetries: 2, 
          baseDelay: 10, // Short delay for test
          maxDelay: 50, 
          exponentialBackoff: false, 
          retryableStatuses: [500, 502, 503, 504] 
        },
      })
    ).rejects.toThrow("Failed to fetch");
    
    expect(global.fetch).toHaveBeenCalledTimes(3); // Initial + 2 retries
    
    jest.useFakeTimers(); // Restore fake timers
  });

  it("should call onRetry callback when retrying", async () => {
    const onRetry = jest.fn();
    const failResponse = createMockResponse("Server Error", 503);
    const successResponse = createMockResponse(JSON.stringify({ success: true }), 200);

    global.fetch = jest
      .fn()
      .mockResolvedValueOnce(failResponse)
      .mockResolvedValueOnce(successResponse);

    const promise = fetchWithRetry("http://test.com/api", {
      retryConfig: {
        maxRetries: 3,
        baseDelay: 100,
        maxDelay: 1000,
        exponentialBackoff: false,
        retryableStatuses: [503],
        onRetry,
      },
    });

    // Advance past the first retry delay
    await jest.advanceTimersByTimeAsync(150);

    await promise;

    expect(onRetry).toHaveBeenCalledTimes(1);
    expect(onRetry).toHaveBeenCalledWith(
      1,
      expect.any(Error),
      expect.any(Number)
    );
  });

  it("should respect custom retry configuration", async () => {
    jest.useRealTimers(); // Use real timers for this test
    
    const failResponse = createMockResponse("Server Error", 500);
    global.fetch = jest.fn().mockResolvedValue(failResponse);

    await expect(
      fetchWithRetry("http://test.com/api", {
        retryConfig: {
          maxRetries: 1,
          baseDelay: 10, // Short delay for test
          maxDelay: 20,
          exponentialBackoff: false,
          retryableStatuses: [500],
        },
      })
    ).rejects.toThrow("HTTP error: 500");
    
    // Initial + 1 retry
    expect(global.fetch).toHaveBeenCalledTimes(2);
    
    jest.useFakeTimers(); // Restore fake timers
  });

  it("should use exponential backoff when enabled", async () => {
    jest.useRealTimers(); // Use real timers for this test
    
    const failResponse = createMockResponse("Server Error", 503);
    global.fetch = jest.fn().mockResolvedValue(failResponse);

    const onRetry = jest.fn();

    try {
      await fetchWithRetry("http://test.com/api", {
        retryConfig: {
          maxRetries: 2, // Reduced for faster test
          baseDelay: 10,
          maxDelay: 100,
          exponentialBackoff: true,
          retryableStatuses: [503],
          onRetry,
        },
      });
    } catch {
      // Expected to throw
    }

    // Verify delays are increasing
    const delays = onRetry.mock.calls.map(
      (call: [number, Error, number]) => call[2]
    );
    
    expect(delays.length).toBeGreaterThanOrEqual(1);
    
    if (delays.length > 1) {
      for (let i = 1; i < delays.length; i++) {
        // Each delay should be roughly double the previous (with jitter)
        // We use a loose check since jitter adds randomness
        expect(delays[i]).toBeGreaterThanOrEqual(delays[i - 1]);
      }
    }
    
    jest.useFakeTimers(); // Restore fake timers
  });

  it("should pass through fetch options", async () => {
    const mockResponse = createMockResponse(JSON.stringify({ success: true }), 200);
    global.fetch = jest.fn().mockResolvedValue(mockResponse);

    await fetchWithRetry("http://test.com/api", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ test: true }),
    });

    expect(global.fetch).toHaveBeenCalledWith("http://test.com/api", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ test: true }),
    });
  });

  it("should cap delay at maxDelay", async () => {
    jest.useRealTimers(); // Use real timers for this test
    
    const failResponse = createMockResponse("Server Error", 503);
    global.fetch = jest.fn().mockResolvedValue(failResponse);

    const onRetry = jest.fn();

    try {
      await fetchWithRetry("http://test.com/api", {
        retryConfig: {
          maxRetries: 3,
          baseDelay: 10,
          maxDelay: 20,
          exponentialBackoff: true,
          retryableStatuses: [503],
          onRetry,
        },
      });
    } catch {
      // Expected to throw
    }

    // Verify no delay exceeds maxDelay (20) + jitter (25% = 5)
    const delays = onRetry.mock.calls.map(
      (call: [number, Error, number]) => call[2]
    );
    delays.forEach((delay: number) => {
      expect(delay).toBeLessThanOrEqual(25); // maxDelay + max jitter
    });
    
    jest.useFakeTimers(); // Restore fake timers
  });
});
