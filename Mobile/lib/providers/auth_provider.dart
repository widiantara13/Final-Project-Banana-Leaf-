import 'package:flutter/material.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

class AuthProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  bool _isLoading = false;
  String? _errorMessage;
  UserProfile? _currentUser;
  bool _isAuthenticated = false;

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  UserProfile? get currentUser => _currentUser;
  bool get isAuthenticated => _isAuthenticated;

  /// Memeriksa apakah user sudah memiliki sesi token yang aktif
  Future<void> checkAuthStatus() async {
    final token = await StorageService.getToken();
    if (token != null && token.isNotEmpty) {
      _isAuthenticated = true;
      try {
        _currentUser = await _apiService.getUserProfile();
      } catch (_) {
        // Jika token sudah kedaluwarsa, bersihkan sesi
        _isAuthenticated = false;
        await StorageService.clearSession();
      }
      notifyListeners();
    }
  }

  /// Proses Login Petani
  Future<bool> login({
    required String email,
    required String password,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final authResponse = await _apiService.login(
        email: email,
        password: password,
      );

      if (authResponse.accessToken.isNotEmpty) {
        _isAuthenticated = true;

        // Ambil data profil setelah login berhasil
        try {
          _currentUser = await _apiService.getUserProfile();
          if (_currentUser?.role != null) {
            await StorageService.saveRole(_currentUser!.role!);
          }
        } catch (_) {
          // Tetap lanjutkan jika profil detail tertunda
        }

        _isLoading = false;
        notifyListeners();
        return true;
      }

      _errorMessage = 'Gagal memproses sesi masuk.';
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Proses Registrasi Petani Baru
  Future<bool> register({
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      await _apiService.register(
        email: email,
        password: password,
        confirmPassword: confirmPassword,
      );

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Memuat data profil terbaru dari server
  Future<void> fetchProfile() async {
    try {
      _currentUser = await _apiService.getUserProfile();
      notifyListeners();
    } catch (_) {
      // Biarkan data lama tetap tampil jika ada gangguan jaringan
    }
  }

  /// Memperbarui data profil pengguna
  Future<bool> updateProfile({
    String? fullName,
    String? phoneNumber,
    String? address,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      await _apiService.updateProfile(
        fullName: fullName,
        phoneNumber: phoneNumber,
        address: address,
      );

      // Perbarui objek profil lokal
      _currentUser = _currentUser?.copyWith(
        fullName: fullName,
        phoneNumber: phoneNumber,
        address: address,
      );

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Memperbarui foto profil pengguna
  Future<bool> updateAvatar(String filePath) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      await _apiService.updateAvatar(filePath);
      await fetchProfile(); // Muat ulang profil dengan url avatar baru
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Membersihkan pesan error
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  /// Keluar / Logout
  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    await _apiService.logout();
    _currentUser = null;
    _isAuthenticated = false;
    _errorMessage = null;
    _isLoading = false;
    notifyListeners();
  }
}

