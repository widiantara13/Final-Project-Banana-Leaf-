import 'package:flutter/material.dart';
import '../models/prediction_model.dart';
import '../services/api_service.dart';

class PredictProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  bool _isLoading = false;
  String? _errorMessage;
  bool _isNotBananaLeaf = false;
  bool _isModelNotReadyError = false;
  PredictionResult? _latestResult;

  bool _isModelReady = true;
  String? _modelStatusMessage;

  // State Riwayat Prediksi
  List<PredictionResult> _historyList = [];
  bool _isHistoryLoading = false;
  bool _sortDateDesc = true;
  String _selectedFilter = 'Semua Tanaman';

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isNotBananaLeaf => _isNotBananaLeaf;
  bool get isModelNotReadyError => _isModelNotReadyError;
  PredictionResult? get latestResult => _latestResult;
  bool get isModelReady => _isModelReady;
  String? get modelStatusMessage => _modelStatusMessage;

  List<PredictionResult> get historyList => _historyList;
  bool get isHistoryLoading => _isHistoryLoading;
  bool get sortDateDesc => _sortDateDesc;
  String get selectedFilter => _selectedFilter;

  /// Daftar riwayat yang sudah disaring (filter) dan diurutkan (sort)
  List<PredictionResult> get filteredHistoryList {
    List<PredictionResult> list = List.from(_historyList);

    // 1. Filter berdasarkan kondisi tanaman
    if (_selectedFilter != 'Semua Tanaman') {
      list = list.where((item) {
        final cond = item.condition.toLowerCase();
        final filter = _selectedFilter.toLowerCase();
        return cond.contains(filter);
      }).toList();
    }

    // 2. Sort berdasarkan tanggal
    list.sort((a, b) {
      final dateA = a.createdAt ?? DateTime.fromMillisecondsSinceEpoch(0);
      final dateB = b.createdAt ?? DateTime.fromMillisecondsSinceEpoch(0);
      if (_sortDateDesc) {
        return dateB.compareTo(dateA); // Terbaru ke terlama (Tanggal ↓)
      } else {
        return dateA.compareTo(dateB); // Terlama ke terbaru (Tanggal ↑)
      }
    });

    return list;
  }

  /// Toggle urutan tanggal (Terbaru <-> Terlama)
  void toggleSortDate() {
    _sortDateDesc = !_sortDateDesc;
    notifyListeners();
  }

  /// Ubah filter kondisi tanaman
  void setFilter(String filter) {
    _selectedFilter = filter;
    notifyListeners();
  }

  /// Memeriksa kesiapan model AI di server
  Future<void> checkModelReadiness() async {
    try {
      final status = await _apiService.checkModelStatus();
      _isModelReady = status['is_ready'] == true;
      _modelStatusMessage = status['message']?.toString();
      notifyListeners();
    } catch (_) {
      // Abaikan error koneksi awal
    }
  }

  /// Mengambil riwayat prediksi dari server
  Future<void> fetchHistory() async {
    _isHistoryLoading = true;
    notifyListeners();

    try {
      _historyList = await _apiService.getPredictionHistory();
      _isHistoryLoading = false;
      notifyListeners();
    } catch (_) {
      _isHistoryLoading = false;
      notifyListeners();
    }
  }

  /// Mengirim foto daun pisang untuk diprediksi
  Future<PredictionResult?> predict(String imagePath) async {
    _isLoading = true;
    _errorMessage = null;
    _isNotBananaLeaf = false;
    _isModelNotReadyError = false;
    notifyListeners();

    try {
      final result = await _apiService.predictLeaf(imagePath);
      _latestResult = result;
      // Sisipkan ke riwayat lokal di posisi paling atas
      _historyList.insert(0, result);
      _isLoading = false;
      notifyListeners();
      return result;
    } on NotBananaLeafException catch (e) {
      _isNotBananaLeaf = true;
      _errorMessage = e.message;
      _isLoading = false;
      notifyListeners();
      return null;
    } on ModelNotReadyException catch (e) {
      _isModelNotReadyError = true;
      _isModelReady = false;
      _modelStatusMessage = e.message;
      _errorMessage = e.message;
      _isLoading = false;
      notifyListeners();
      return null;
    } catch (e) {
      final msg = e.toString().replaceAll('Exception: ', '');
      if (msg.toLowerCase().contains('bukan daun pisang')) {
        _isNotBananaLeaf = true;
      }
      if (msg.toLowerCase().contains('belum aktif') ||
          msg.toLowerCase().contains('belum di load') ||
          msg.toLowerCase().contains('belum dimuat') ||
          msg.toLowerCase().contains('belum siap')) {
        _isModelNotReadyError = true;
        _isModelReady = false;
        _modelStatusMessage = msg;
      }
      _errorMessage = msg;
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  /// Menghapus data riwayat prediksi
  Future<bool> deletePrediction(int id) async {
    try {
      await _apiService.deletePrediction(id);
      _historyList.removeWhere((item) => item.id == id);
      if (_latestResult?.id == id) {
        _latestResult = null;
      }
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  /// Membersihkan status dan hasil prediksi
  void reset() {
    _latestResult = null;
    _errorMessage = null;
    _isNotBananaLeaf = false;
    _isModelNotReadyError = false;
    _isLoading = false;
    notifyListeners();
  }
}
