class ApiConstants {
  /// Base URL backend FastAPI.
  /// - Saat memakai kabel USB dengan `adb reverse tcp:8000 tcp:8000`: gunakan 'http://localhost:8000'
  /// - Saat memakai Android Emulator: gunakan 'http://10.0.2.2:8000'
  /// - Saat memakai Wi-Fi LAN: gunakan IP laptop, contoh 'http://192.168.1.xxx:8000'
  static const String baseUrl = 'http://192.168.1.5:8000';

  // Auth endpoints
  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register/';
  static const String logoutEndpoint = '/auth/logout/';

  // Predict & Model status endpoints
  static const String predictStatusEndpoint = '/predict/status';
  static const String predictAddEndpoint = '/predict/add';
  static const String predictShowEndpoint = '/predict/show';
  static String predictDeleteEndpoint(int id) => '/predict/delete/$id';

  // Leaf conditions info & Encyclopedia
  static const String leafShowEndpoint = '/leaf/show';

  // Profile endpoints
  static const String profileDetailEndpoint = '/profile/detail';
  static const String profileUpdateEndpoint = '/profile/update';
  static const String profileUpdateImageEndpoint = '/profile/update-image';

  // Static files URL helper
  static String getStaticUrl(String path) {
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path;
    }
    final cleanPath = path.startsWith('/') ? path : '/$path';
    return '$baseUrl$cleanPath';
  }
}

