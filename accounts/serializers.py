from django.contrib.auth import get_user_model
from rest_framework import serializers
from companies.models import Company


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField()
    company_domain = serializers.CharField()
    company_email = serializers.EmailField()
    business_type = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "company_name",
            "company_domain",
            "company_email",
            "business_type",
        ]

    def create(self, validated_data):
        if Company.objects.filter(domain=validated_data["company_domain"]).exists():
            raise serializers.ValidationError({"company_domain": "Company domain already exists."})
        
        if Company.objects.filter(company_email=validated_data["company_email"]).exists():
            raise serializers.ValidationError({"company_email": "Company email already exists."})


        company = Company.objects.create(
            name=validated_data.pop("company_name"),
            domain=validated_data.pop("company_domain"),
            company_email=validated_data.pop("company_email"),
            business_type=validated_data.pop("business_type"),
        )
        validated_data["email"] = company.company_email
        return User.objects.create_user(company=company, **validated_data)


class LoginSerializer(serializers.Serializer):
    company_email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        company_email = attrs.get("company_email")
        password = attrs.get("password")

        user = User.objects.filter(email__iexact=company_email).first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs
