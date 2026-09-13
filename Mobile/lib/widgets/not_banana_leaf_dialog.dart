import 'package:flutter/material.dart';
import '../constants/app_colors.dart';

/// Popup dialog peringatan saat model AI mendeteksi gambar input bukan daun pisang.
/// Sesuai rancangan wireframe:
/// - Judul: "Peringatan Gambar"
/// - Ikon: Kotak melengkung berisi tanda silang merah (X)
/// - Judul Pesan: "Gambar yang Anda kirimkan bukan daun pisang!"
/// - Sub-pesan: "Silakan inputkan gambar daun pisang"
/// - Tombol: Pill button "Coba Lagi"
class NotBananaLeafDialog extends StatelessWidget {
  final VoidCallback? onRetry;

  const NotBananaLeafDialog({
    super.key,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
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
            // 1. JUDUL "Peringatan Gambar"
            // ==========================================
            const Text(
              'Peringatan Gambar',
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
            // 2. KOTAK IKON SILANG MERAH (X)
            // ==========================================
            Container(
              width: 96,
              height: 96,
              decoration: BoxDecoration(
                color: const Color(0xFFFEF2F2), // Soft red background
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                  color: const Color(0xFFFCA5A5), // Red tinted border
                  width: 2,
                ),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFFDC2626).withOpacity(0.08),
                    blurRadius: 16,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const Center(
                child: Icon(
                  Icons.close_rounded,
                  size: 62,
                  color: Color(0xFFDC2626), // Thick red cross mark
                ),
              ),
            ),

            const SizedBox(height: 22),

            // ==========================================
            // 3. PESAN UTAMA
            // ==========================================
            const Text(
              'Gambar yang Anda kirimkan\nbukan daun pisang!',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
                height: 1.35,
              ),
            ),

            const SizedBox(height: 10),

            // ==========================================
            // 4. SUB-PESAN / PETUNJUK
            // ==========================================
            const Text(
              'Silakan inputkan gambar daun pisang',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: AppColors.textSecondary,
              ),
            ),

            const SizedBox(height: 24),

            // ==========================================
            // 5. TOMBOL "Coba Lagi" (Pill Button)
            // ==========================================
            SizedBox(
              width: double.infinity,
              height: 46,
              child: OutlinedButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  onRetry?.call();
                },
                style: OutlinedButton.styleFrom(
                  backgroundColor: const Color(0xFFFEE2E2), // Soft red background
                  foregroundColor: const Color(0xFFDC2626), // Red text
                  side: const BorderSide(
                    color: Color(0xFFF87171), // Red outline
                    width: 1.2,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(24),
                  ),
                  padding: EdgeInsets.zero,
                ),
                child: const Text(
                  'Coba Lagi',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFFDC2626),
                    letterSpacing: 0.3,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Helper function untuk menampilkan dialog Peringatan Gambar Bukan Daun Pisang
Future<void> showNotBananaLeafDialog({
  required BuildContext context,
  VoidCallback? onRetry,
}) {
  return showDialog(
    context: context,
    barrierDismissible: true,
    builder: (ctx) => NotBananaLeafDialog(onRetry: onRetry),
  );
}

