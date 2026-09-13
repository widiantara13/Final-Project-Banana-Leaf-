import 'dart:io';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../constants/api_constants.dart';
import '../constants/app_colors.dart';
import '../models/prediction_model.dart';
import '../providers/predict_provider.dart';

/// Popup dialog detail hasil prediksi daun pisang petani
/// Sesuai wireframe:
/// - Judul "Detail Prediksi"
/// - Gambar daun pisang besar
/// - Kondisi dan akurasi (misal: "Healthy (99%)")
/// - Tanggal dan Waktu
/// - Tombol pill "kembali" dan "hapus"
class PredictionDetailDialog extends StatefulWidget {
  final PredictionResult prediction;
  final String? localImagePath;
  final VoidCallback? onDeleted;

  const PredictionDetailDialog({
    super.key,
    required this.prediction,
    this.localImagePath,
    this.onDeleted,
  });

  @override
  State<PredictionDetailDialog> createState() => _PredictionDetailDialogState();
}

class _PredictionDetailDialogState extends State<PredictionDetailDialog> {
  bool _isDeleting = false;

  String _formatDate(DateTime? dateTime) {
    final dt = dateTime?.toLocal() ?? DateTime.now();
    try {
      return DateFormat('dd MMM yyyy').format(dt);
    } catch (_) {
      return '-';
    }
  }

  String _formatTime(DateTime? dateTime) {
    final dt = dateTime?.toLocal() ?? DateTime.now();
    try {
      return DateFormat('HH:mm').format(dt);
    } catch (_) {
      return '-';
    }
  }

  Future<void> _handleDelete() async {
    final predId = widget.prediction.id;
    if (predId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('ID prediksi tidak valid untuk dihapus.'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    // Tampilkan konfirmasi penghapusan
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        backgroundColor: AppColors.cardSurface,
        title: const Text(
          'Hapus Prediksi?',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: AppColors.textPrimary,
            fontSize: 18,
          ),
        ),
        content: const Text(
          'Apakah Anda yakin ingin menghapus hasil prediksi ini? Data dan foto akan dihapus secara permanen.',
          style: TextStyle(
            color: AppColors.textSecondary,
            fontSize: 14,
          ),
        ),
        actionsPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text(
              'Batal',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: AppColors.textSecondary,
              ),
            ),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFDC2626),
              foregroundColor: Colors.white,
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Text(
              'Hapus',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );

    if (confirm != true || !mounted) return;

    setState(() {
      _isDeleting = true;
    });

    final provider = Provider.of<PredictProvider>(context, listen: false);
    final success = await provider.deletePrediction(predId);

    if (!mounted) return;

    setState(() {
      _isDeleting = false;
    });

    if (success) {
      Navigator.of(context).pop(); // Tutup dialog detail
      widget.onDeleted?.call();

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Row(
            children: [
              Icon(Icons.check_circle_rounded, color: Colors.white),
              SizedBox(width: 10),
              Text(
                'Riwayat prediksi berhasil dihapus',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
            ],
          ),
          backgroundColor: AppColors.primary,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.error_outline_rounded, color: Colors.white),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  provider.errorMessage ?? 'Gagal menghapus riwayat prediksi.',
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
          backgroundColor: AppColors.error,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final pred = widget.prediction;
    final dateStr = _formatDate(pred.createdAt);
    final timeStr = _formatTime(pred.createdAt);

    // Persiapkan gambar (lokal atau jaringan)
    Widget imageWidget;
    if (widget.localImagePath != null && File(widget.localImagePath!).existsSync()) {
      imageWidget = Image.file(
        File(widget.localImagePath!),
        fit: BoxFit.cover,
      );
    } else if (pred.imagePath != null && pred.imagePath!.isNotEmpty) {
      imageWidget = Image.network(
        ApiConstants.getStaticUrl(pred.imagePath!),
        fit: BoxFit.cover,
        errorBuilder: (_, __, ___) => Center(
          child: Icon(
            Icons.image_outlined,
            size: 80,
            color: AppColors.primary.withOpacity(0.5),
          ),
        ),
        loadingBuilder: (_, child, loadingProgress) {
          if (loadingProgress == null) return child;
          return const Center(
            child: CircularProgressIndicator(
              color: AppColors.primary,
              strokeWidth: 2,
            ),
          );
        },
      );
    } else {
      imageWidget = Center(
        child: Icon(
          Icons.image_outlined,
          size: 80,
          color: AppColors.primary.withOpacity(0.5),
        ),
      );
    }

    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 360),
        decoration: BoxDecoration(
          color: AppColors.cardSurface,
          borderRadius: BorderRadius.circular(28),
          border: Border.all(color: AppColors.cardBorder, width: 1.2),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.12),
              blurRadius: 28,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        padding: const EdgeInsets.fromLTRB(20, 22, 20, 20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // ==========================================
            // 1. JUDUL "Detail Prediksi"
            // ==========================================
            const Text(
              'Detail Prediksi',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
                letterSpacing: 0.3,
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 18),

            // ==========================================
            // 2. GAMBAR DAUN PISANG
            // ==========================================
            Container(
              width: double.infinity,
              height: 190,
              decoration: BoxDecoration(
                color: AppColors.inputBackground,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: AppColors.cardBorder,
                  width: 1.5,
                ),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(20),
                child: imageWidget,
              ),
            ),

            const SizedBox(height: 18),

            // ==========================================
            // 3. HASIL PREDIKSI (Kondisi & Akurasi %)
            // ==========================================
            Text(
              '${pred.condition} (${pred.confidence.toStringAsFixed(0)}%)',
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: AppColors.primaryForest,
                letterSpacing: 0.2,
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 6),

            // ==========================================
            // 4. TANGGAL
            // ==========================================
            Text(
              'Tanggal: $dateStr',
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 3),

            // ==========================================
            // 5. WAKTU
            // ==========================================
            Text(
              'Waktu: $timeStr',
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 24),

            // ==========================================
            // 6. TOMBOL AKSI: "kembali" & "hapus" (Pill Buttons)
            // ==========================================
            Row(
              children: [
                // Tombol "kembali"
                Expanded(
                  child: SizedBox(
                    height: 44,
                    child: ElevatedButton(
                      onPressed: _isDeleting ? null : () => Navigator.of(context).pop(),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF4B5563), // Dark Slate Gray sesuai wireframe
                        foregroundColor: Colors.white,
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(24),
                        ),
                        padding: EdgeInsets.zero,
                      ),
                      child: const Text(
                        'kembali',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.3,
                        ),
                      ),
                    ),
                  ),
                ),

                const SizedBox(width: 14),

                // Tombol "hapus"
                Expanded(
                  child: SizedBox(
                    height: 44,
                    child: OutlinedButton(
                      onPressed: _isDeleting ? null : _handleDelete,
                      style: OutlinedButton.styleFrom(
                        backgroundColor: const Color(0xFFFEE2E2), // Soft red background
                        foregroundColor: const Color(0xFFDC2626), // Deep red text
                        side: const BorderSide(
                          color: Color(0xFFF87171), // Red outline
                          width: 1.2,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(24),
                        ),
                        padding: EdgeInsets.zero,
                      ),
                      child: _isDeleting
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFDC2626)),
                              ),
                            )
                          : const Text(
                              'hapus',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFFDC2626),
                                letterSpacing: 0.3,
                              ),
                            ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

/// Helper function untuk memanggil dialog Detail Prediksi dari mana saja
Future<void> showPredictionDetailDialog({
  required BuildContext context,
  required PredictionResult prediction,
  String? localImagePath,
  VoidCallback? onDeleted,
}) {
  return showDialog(
    context: context,
    barrierDismissible: true,
    builder: (ctx) => PredictionDetailDialog(
      prediction: prediction,
      localImagePath: localImagePath,
      onDeleted: onDeleted,
    ),
  );
}

