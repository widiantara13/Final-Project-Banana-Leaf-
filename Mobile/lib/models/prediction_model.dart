class PredictionResult {
  final int? id;
  final String? imagePath;
  final String condition;
  final double confidence;
  final String? real;
  final String? rawMessage;
  final DateTime? createdAt;

  PredictionResult({
    this.id,
    this.imagePath,
    required this.condition,
    required this.confidence,
    this.real,
    this.rawMessage,
    this.createdAt,
  });

  factory PredictionResult.fromJson(Map<String, dynamic> json) {
    DateTime? parseDate(dynamic dateVal) {
      if (dateVal == null) return null;
      if (dateVal is DateTime) return dateVal;
      try {
        return DateTime.parse(dateVal.toString());
      } catch (_) {
        return null;
      }
    }

    if (json.containsKey('data') && json['data'] != null) {
      final data = json['data'];
      return PredictionResult(
        id: data['id'],
        imagePath: data['image_path'],
        condition: data['condition'] ?? json['real'] ?? 'Unknown',
        confidence: (data['confidence'] as num?)?.toDouble() ?? 0.0,
        real: json['real'],
        createdAt: parseDate(data['created_at']),
      );
    }

    return PredictionResult(
      id: json['id'],
      imagePath: json['image_path'],
      condition: json['condition'] ?? 'Unknown',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      rawMessage: json['detail'],
      createdAt: parseDate(json['created_at']),
    );
  }
}

/// Exception khusus saat model deteksi AI mendeteksi gambar bukan daun pisang
class NotBananaLeafException implements Exception {
  final String message;
  NotBananaLeafException([this.message = 'Gambar yang Anda kirimkan bukan daun pisang!']);

  @override
  String toString() => message;
}

/// Exception khusus saat model AI belum dimuat / belum aktif di backend
class ModelNotReadyException implements Exception {
  final String message;
  ModelNotReadyException([this.message = 'Model deteksi belum aktif, mohon tunggu beberapa saat lagi atau hubungi administrator.']);

  @override
  String toString() => message;
}
