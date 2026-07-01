import heapq

queue = []

heapq.heappush(queue, (100, 1))
heapq.heappush(queue, (10, 1))
heapq.heappush(queue, (0, 1))

print(queue)