class AuthResponse {
  final String accessToken;
  final String tokenType;

  AuthResponse({
    required this.accessToken,
    required this.tokenType,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] ?? '',
      tokenType: json['token_type'] ?? 'bearer',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'token_type': tokenType,
    };
  }
}

class UserProfile {
  final int? userId;
  final String? email;
  final String? role;
  final bool isActive;
  final String? fullName;
  final String? phoneNumber;
  final String? address;
  final String? avatar;

  UserProfile({
    this.userId,
    this.email,
    this.role,
    this.isActive = true,
    this.fullName,
    this.phoneNumber,
    this.address,
    this.avatar,
  });

  String? get username => fullName;

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      userId: json['user_id'] ?? json['id'],
      email: json['email'],
      role: json['role'],
      isActive: json['is_active'] ?? true,
      fullName: json['full_name'] ?? json['username'],
      phoneNumber: json['phone_number'],
      address: json['address'],
      avatar: json['avatar'] ?? json['profile_image'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'email': email,
      'role': role,
      'is_active': isActive,
      'full_name': fullName,
      'phone_number': phoneNumber,
      'address': address,
      'avatar': avatar,
    };
  }

  UserProfile copyWith({
    int? userId,
    String? email,
    String? role,
    bool? isActive,
    String? fullName,
    String? phoneNumber,
    String? address,
    String? avatar,
  }) {
    return UserProfile(
      userId: userId ?? this.userId,
      email: email ?? this.email,
      role: role ?? this.role,
      isActive: isActive ?? this.isActive,
      fullName: fullName ?? this.fullName,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      address: address ?? this.address,
      avatar: avatar ?? this.avatar,
    );
  }
}
