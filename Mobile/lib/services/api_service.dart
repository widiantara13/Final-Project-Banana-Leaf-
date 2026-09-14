import 'dart:io';
import 'package:dio/dio.dart';
import '../constants/api_constants.dart';
import '../models/user_model.dart';
import '../models/prediction_model.dart';
import 'storage_service.dart';

class ApiService {
  late final Dio _dio;

  ApiService() {
    final platformName = Platform.isAndroid
        ? 'Android'
        : (Platform.isIOS ? 'iOS' : 'Mobile');

    _dio = Dio(
      BaseOptions(
        baseUrl: ApiConstants.baseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 20),
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'BananaLeaf-Mobile/1.0 ($platformName; Mobile)',
        },
      ),
    );

    // Menambahkan Interceptor untuk menyisipkan Bearer Token secara otomatis
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await StorageService.getToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (DioException e, handler) {
          return handler.next(e);
        },
      ),
    );
  }

  /// Autentikasi Login Petani
  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    try {
      // Backend FastAPI menggunakan OAuth2PasswordRequestForm
      final formData = FormData.fromMap({
        'username': email.trim(),
        'password': password,
      });

      final response = await _dio.post(
        ApiConstants.loginEndpoint,
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
        ),
      );

      if (response.statusCode == 200 && response.data != null) {
        final authResponse = AuthResponse.fromJson(response.data);
        await StorageService.saveToken(authResponse.accessToken);
        await StorageService.saveEmail(email.trim());
        return authResponse;
      } else {
        throw Exception('Gagal masuk. Silakan periksa kembali email dan password Anda.');
      }
    } on DioException catch (e) {
      String errorMessage = 'Terjadi kesalahan saat menghubungi server.';
      if (e.response != null && e.response?.data != null) {
        final data = e.response?.data;
        if (data is Map && data.containsKey('detail')) {
          errorMessage = data['detail'].toString();
        }
      } else if (e.type == DioExceptionType.connectionTimeout ||
                 e.type == DioExceptionType.receiveTimeout) {
        errorMessage = 'Koneksi ke server terputus (waktu habis). Pastikan server backend berjalan.';
      } else if (e.type == DioExceptionType.connectionError) {
        errorMessage = 'Tidak dapat terhubung ke server backend (${ApiConstants.baseUrl}). Pastikan port 8000 aktif.';
      }
      throw Exception(errorMessage);
    } catch (e) {
      throw Exception(e.toString().replaceAll('Exception: ', ''));
    }
  }

  /// Pendaftaran Akun Petani Baru
  Future<String> register({
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    try {
      final response = await _dio.post(
        ApiConstants.registerEndpoint,
        data: {
          'email': email.trim(),
          'password': password,
          'confirm_password': confirmPassword,
        },
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        final message = response.data?['message'] ?? 'Pendaftaran berhasil!';
        return message.toString();
      } else {
        throw Exception('Gagal melakukan pendaftaran.');
      }
    } on DioException catch (e) {
      String errorMessage = 'Terjadi kesalahan saat pendaftaran.';
      if (e.response != null && e.response?.data != null) {
        final data = e.response?.data;
        if (data is Map && data.containsKey('detail')) {
          errorMessage = data['detail'].toString();
        }
      } else if (e.type == DioExceptionType.connectionTimeout ||
                 e.type == DioExceptionType.receiveTimeout) {
        errorMessage = 'Koneksi ke server terputus. Pastikan server backend berjalan.';
      } else if (e.type == DioExceptionType.connectionError) {
        errorMessage = 'Tidak dapat terhubung ke server backend.';
      }
      throw Exception(errorMessage);
    } catch (e) {
      throw Exception(e.toString().replaceAll('Exception: ', ''));
    }
  }

  /// Mendapatkan detail profil user yang sedang login
  Future<UserProfile> getUserProfile() async {
    try {
      final response = await _dio.get(ApiConstants.profileDetailEndpoint);
      if (response.statusCode == 200 && response.data != null) {
        return UserProfile.fromJson(response.data);
      }
      throw Exception('Gagal memuat profil pengguna.');
    } on DioException catch (e) {
      final detail = e.response?.data?['detail'] ?? 'Gagal mengambil data profil';
      throw Exception(detail);
    }
  }

  /// Memperbarui data profil pengguna
  Future<void> updateProfile({
    String? fullName,
    String? phoneNumber,
    String? address,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (fullName != null) data['full_name'] = fullName.trim();
      if (phoneNumber != null) data['phone_number'] = phoneNumber.trim();
      if (address != null) data['address'] = address.trim();

      await _dio.patch(
        ApiConstants.profileUpdateEndpoint,
        data: data,
      );
    } on DioException catch (e) {
      final detail = e.response?.data?['detail'] ?? 'Gagal memperbarui profil.';
      throw Exception(detail);
    } catch (e) {
      throw Exception(e.toString().replaceAll('Exception: ', ''));
    }
  }

  /// Mengunggah & memperbarui foto profil (avatar)
  Future<void> updateAvatar(String filePath) async {
    try {
      final fileName = filePath.split('/').last;
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          filePath,
          filename: fileName,
        ),
      });

      await _dio.put(
        ApiConstants.profileUpdateImageEndpoint,
        data: formData,
      );
    } on DioException catch (e) {
      final detail = e.response?.data?['detail'] ?? 'Gagal mengunggah foto profil.';
      throw Exception(detail);
    } catch (e) {
      throw Exception(e.toString().replaceAll('Exception: ', ''));
    }
  }

  /// Mengirim foto daun pisang untuk prediksi klasifikasi penyakit
  Future<PredictionResult> predictLeaf(String filePath) async {
    try {
      final fileName = filePath.split('/').last;
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          filePath,
          filename: fileName,
        ),
      });

      final response = await _dio.post(
        ApiConstants.predictAddEndpoint,
        data: formData,
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        final data = response.data;
        if (data is Map &&
            data['detail'] != null &&
            data['detail'].toString().toLowerCase().contains('bukan daun pisang')) {
          throw NotBananaLeafException(data['detail'].toString());
        }
        return PredictionResult.fromJson(data);
      }
      throw Exception('Gagal melakukan prediksi.');
    } on NotBananaLeafException {
      rethrow;
    } on ModelNotReadyException {
      rethrow;
    } on DioException catch (e) {
      if (e.response != null && e.response?.statusCode == 503) {
        final msg = e.response?.data?['detail']?.toString() ??
            'Model deteksi belum aktif, mohon tunggu beberapa saat lagi atau hubungi administrator.';
        throw ModelNotReadyException(msg);
      }
      final detail = e.response?.data?['detail']?.toString() ?? 'Gagal memproses gambar daun pisang.';
      if (detail.toLowerCase().contains('bukan daun pisang')) {
        throw NotBananaLeafException(detail);
      }
      if (detail.toLowerCase().contains('belum aktif') ||
          detail.toLowerCase().contains('belum di load') ||
          detail.toLowerCase().contains('belum dimuat') ||
          detail.toLowerCase().contains('belum siap')) {
        throw ModelNotReadyException(detail);
      }
      throw Exception(detail);
    } catch (e) {
      if (e is NotBananaLeafException || e is ModelNotReadyException) rethrow;
      throw Exception(e.toString().replaceAll('Exception: ', ''));
    }
  }

  /// Mengambil daftar riwayat prediksi petani
  Future<List<PredictionResult>> getPredictionHistory() async {
    try {
      final response = await _dio.get(ApiConstants.predictShowEndpoint);
      if (response.statusCode == 200 && response.data != null) {
        final list = response.data as List;
        return list.map((item) => PredictionResult.fromJson(item)).toList();
      }
      return [];
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return []; // Riwayat kosong
      }
      final detail = e.response?.data?['detail'] ?? 'Gagal memuat riwayat prediksi.';
      throw Exception(detail);
    } catch (e) {
      throw Exception(e.toString().replaceAll('Exception: ', ''));
    }
  }

  /// Menghapus data riwayat prediksi berdasarkan ID
  Future<void> deletePrediction(int idPredict) async {
    try {
      final response = await _dio.delete(ApiConstants.predictDeleteEndpoint(idPredict));
      if (response.statusCode != 200) {
        throw Exception('Gagal menghapus prediksi.');
      }
    } on DioException catch (e) {
      final detail = e.response?.data?['detail'] ?? 'Gagal menghapus riwayat prediksi.';
      throw Exception(detail);
    } catch (e) {
      throw Exception(e.toString().replaceAll('Exception: ', ''));
    }
  }

  /// Memeriksa kesiapan model AI di server
  Future<Map<String, dynamic>> checkModelStatus() async {
    try {
      final response = await _dio.get(ApiConstants.predictStatusEndpoint);
      if (response.statusCode == 200 && response.data != null) {
        return Map<String, dynamic>.from(response.data);
      }
      return {'is_ready': false, 'message': 'Status model tidak tersedia'};
    } catch (e) {
      return {'is_ready': false, 'message': 'Gagal memeriksa status AI'};
    }
  }

  /// Logout dari server
  Future<void> logout() async {
    try {
      await _dio.post(ApiConstants.logoutEndpoint);
    } catch (_) {
      // Abaikan error jaringan saat logout, tetap hapus sesi lokal
    } finally {
      await StorageService.clearSession();
    }
  }
}

