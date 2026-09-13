import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../constants/app_colors.dart';
import '../providers/predict_provider.dart';

/// Popup dialog peringatan saat model AI belum dimuat / belum aktif di backend.
/// Sesuai permintaan: pesan disampaikan lewat pop up.
class ModelNotReadyDialog extends StatefulWidget {
  final String? message;
  final VoidCallback? onDismiss;

  const ModelNotReadyDialog({
    super.key,
    this.message,
    this.onDismiss,
  });

  @override
  State<ModelNotReadyDialog> createState() => _ModelNotReadyDialogState();
}

class _ModelNotReadyDialogState extends State<ModelNotReadyDialog> {
  bool _isChecking = false;

  Future<void> _checkAgain() async {
    setState(() {
      _isChecking = true;
    });

    final provider = Provider.of<PredictProvider>(context, listen: false);
    await provider.checkModelReadiness();

    if (!mounted) return;

    setState(() {
      _isChecking = false;
    });

    if (provider.isModelReady) {
      Navigator.of(context).pop();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Row(
            children: [
              Icon(Icons.check_circle_rounded, color: Colors.white),
              SizedBox(width: 10),
              Text(
                'Model AI sudah siap digunakan!',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
            ],
          ),
          backgroundColor: AppColors.primary,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final displayMessage = widget.message ??
        'Model deteksi belum aktif, mohon tunggu beberapa saat lagi atau hubungi administrator.';

    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 340),
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
        padding: const EdgeInsets.fromLTRB(22, 24, 22, 22),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // ==========================================
            // 1. JUDUL "Peringatan Sistem"
            // ==========================================
            const Text(
              'Peringatan Sistem',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
                letterSpacing: 0.3,
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 22),

            // ==========================================
            // 2. KOTAK IKON MODEL AI (Amber / Kuning Pisang)
            // ==========================================
            Container(
              width: 96,
              height: 96,
              decoration: BoxDecoration(
                color: AppColors.bananaCream,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                  color: AppColors.bananaYellow,
                  width: 2,
                ),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.bananaGold.withOpacity(0.15),
                    blurRadius: 16,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const Center(
                child: Icon(
                  Icons.psychology_alt_outlined,
                  size: 58,
                  color: AppColors.bananaGold,
                ),
              ),
            ),

            const SizedBox(height: 22),

            // ==========================================
            // 3. JUDUL PESAN
            // ==========================================
            const Text(
              'Model AI Belum Aktif',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),

            const SizedBox(height: 10),

            // ==========================================
            // 4. PESAN DARI BACKEND
            // ==========================================
            Text(
              displayMessage,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: AppColors.textSecondary,
                height: 1.4,
              ),
            ),

            const SizedBox(height: 24),

            // ==========================================
            // 5. TOMBOL AKSI PILL
            // ==========================================
            Row(
              children: [
                // Tombol Tutup
                Expanded(
                  child: SizedBox(
                    height: 44,
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.of(context).pop();
                        widget.onDismiss?.call();
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF4B5563), // Slate Gray
                        foregroundColor: Colors.white,
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(24),
                        ),
                        padding: EdgeInsets.zero,
                      ),
                      child: const Text(
                        'Tutup',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ),

                const SizedBox(width: 12),

                // Tombol Cek Lagi
                Expanded(
                  child: SizedBox(
                    height: 44,
                    child: ElevatedButton(
                      onPressed: _isChecking ? null : _checkAgain,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        foregroundColor: Colors.white,
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(24),
                        ),
                        padding: EdgeInsets.zero,
                      ),
                      child: _isChecking
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : const Text(
                              'Cek Lagi',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
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

/// Helper function untuk memunculkan pop-up Model AI Belum Aktif
Future<void> showModelNotReadyDialog({
  required BuildContext context,
  String? message,
  VoidCallback? onDismiss,
}) {
  return showDialog(
    context: context,
    barrierDismissible: true,
    builder: (ctx) => ModelNotReadyDialog(
      message: message,
      onDismiss: onDismiss,
    ),
  );
}

