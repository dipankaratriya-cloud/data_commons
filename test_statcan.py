"""Test script to extract metadata from Statistics Canada dataset."""
import os
from dotenv import load_dotenv
from src.orchestrator import MetadataOrchestrator
import json

def main():
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')

    if not api_key:
        print("❌ Error: GROQ_API_KEY not found")
        return

    url = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810020401&pickMembers%5B0%5D=1.1&cubeTimeFrame.startMonth=04&cubeTimeFrame.startYear=2024&cubeTimeFrame.endMonth=08&cubeTimeFrame.endYear=2025&referencePeriods=20240401%2C20250801"

    print("=" * 80)
    print("  Statistics Canada Metadata Extraction")
    print("=" * 80)
    print(f"\n📎 URL: {url[:100]}...")
    print("\n🔧 Initializing orchestrator...")

    orchestrator = MetadataOrchestrator(api_key)

    print("🌐 Extracting metadata (using hybrid scraping + Groq)...")
    print("⏳ This may take a moment...\n")

    try:
        results = orchestrator.extract_metadata(url)

        print("=" * 80)
        print("  EXTRACTION RESULTS")
        print("=" * 80)

        # License Information
        if results.get('license'):
            print("\n📄 LICENSE INFORMATION:")
            print("-" * 80)
            license_data = results['license']
            if license_data.get('best_match'):
                best = license_data['best_match']
                print(f"License Type: {best.get('license_type', 'Not found')}")
                print(f"License URL: {best.get('license_url', 'Not found')}")
                print(f"Confidence: {best.get('confidence', 'Unknown')}")
            validation = results['validation']['license']
            print(f"Quality Score: {validation.get('quality_score', 0)}/100")
            if validation.get('warnings'):
                print(f"Warnings: {', '.join(validation['warnings'])}")

        # Place Information
        if results.get('place'):
            print("\n🌍 PLACE INFORMATION:")
            print("-" * 80)
            place_data = results['place']

            # Geographic coverage
            geo = place_data.get('geographic_coverage', {})
            if geo.get('countries'):
                print(f"Countries: {', '.join(geo['countries'])}")
            if geo.get('regions'):
                print(f"Regions: {', '.join(geo['regions'][:5])}")  # First 5

            # Place types
            if place_data.get('place_types'):
                print(f"Place Types: {', '.join(place_data['place_types'])}")

            # ID systems
            id_sys = place_data.get('place_id_systems', {})
            if id_sys.get('systems'):
                print(f"ID Systems: {', '.join(id_sys['systems'])}")
            if id_sys.get('resolution_method'):
                print(f"Resolution Method: {id_sys['resolution_method']}")

            validation = results['validation']['place']
            print(f"Quality Score: {validation.get('quality_score', 0)}/100")

        # Temporal Information
        if results.get('temporal'):
            print("\n📅 TEMPORAL INFORMATION:")
            print("-" * 80)
            temporal_data = results['temporal']

            # Coverage period
            coverage = temporal_data.get('coverage_period', {})
            if coverage.get('start_date'):
                print(f"Start Date: {coverage['start_date']}")
            if coverage.get('end_date'):
                print(f"End Date: {coverage['end_date']}")

            # Update frequency
            freq = temporal_data.get('update_frequency', {})
            if freq.get('frequency'):
                print(f"Update Frequency: {freq['frequency']}")

            # Temporal resolution
            if temporal_data.get('temporal_resolution'):
                print(f"Temporal Resolution: {temporal_data['temporal_resolution']}")

            # Last updated
            if temporal_data.get('last_updated'):
                print(f"Last Updated: {temporal_data['last_updated']}")

            validation = results['validation']['temporal']
            print(f"Quality Score: {validation.get('quality_score', 0)}/100")

        # Overall Summary
        print("\n" + "=" * 80)
        print("  SUMMARY")
        print("=" * 80)
        print(f"Overall Quality Score: {results['validation']['overall_score']}/100")
        print(f"Execution Time: {results['execution_time']:.2f} seconds")

        if results.get('errors'):
            print(f"\n⚠️ Errors encountered:")
            for error in results['errors']:
                print(f"  - {error}")

        # Save to file
        output_file = "statcan_extraction_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Full results saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Error during extraction: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
