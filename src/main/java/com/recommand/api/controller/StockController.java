package com.recommand.api.controller;

import java.util.HashMap;
import java.util.Map;
import org.springframework.http.ResponseEntity;


@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = "*")
public class StockController {

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "healthy");
        response.put("service", "RecommandApi");
        response.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(response);
    }

    @GetMapping("/stocks")
    public ResponseEntity<Map<String, Object>> getStocks(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        Map<String, Object> response = new HashMap<>();
        response.put("page", page);
        response.put("size", size);
        response.put("stocks", new Object[]{});
        response.put("total", 0);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/stocks/{code}")
    public ResponseEntity<Map<String, String>> getStock(@PathVariable String code) {
        Map<String, String> response = new HashMap<>();
        response.put("code", code);
        response.put("name", "종목명");
        response.put("message", "상세 정보는 구현 예정입니다.");
        return ResponseEntity.ok(response);
    }

    @GetMapping("/recommendations")
    public ResponseEntity<Map<String, Object>> getRecommendations() {
        Map<String, Object> response = new HashMap<>();
        response.put("recommendations", new Object[]{});
        response.put("total", 0);
        response.put("message", "AI 추천 기능은 구현 예정입니다.");
        return ResponseEntity.ok(response);
    }

    @GetMapping("/news")
    public ResponseEntity<Map<String, Object>> getNews(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        Map<String, Object> response = new HashMap<>();
        response.put("page", page);
        response.put("size", size);
        response.put("news", new Object[]{});
        response.put("total", 0);
        return ResponseEntity.ok(response);
    }
}
