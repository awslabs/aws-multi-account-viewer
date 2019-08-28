export const Container = {
  fontFamily: `"Amazon Ember", "Helvetica Neue", sans-serif`,
  fontWeight: '400',
  };
  
  export const FormContainer = {
    textAlign: 'center',
    marginTop: '0px',
    margin: '0% auto 50px',
    backgroundColor:"#2e303a"
  };
  
  export const FormSection = {
    height: "100%",
    marginTop: "3%",
    position: "relative",
    marginBottom: "200px",
    backgroundColor: "#fff",
    padding: "35px 40px",
    textAlign: "left",
    display: "inline-block",
    borderRadius: "20px",
    boxShadow: "1px 1px 4px 0 rgba(255,255,255,0.5)"
  };
  
  export const FormField = {
    marginBottom: "22px"
  };

  export const SectionHeader = {};
  export const SectionBody = {};
  export const SectionFooter = {};
  export const SectionFooterPrimaryContent = {};
  export const SectionFooterSecondaryContent = {};
  export const Input = {borderColor:"#4286f4"};
  export const Button = {backgroundColor:"#4286f4", padding: "10px"};
  export const PhotoPickerButton = {};
  export const PhotoPlaceholder = {};
  export const SignInButton = {};
  export const SignInButtonIcon = {};
  export const SignInButtonContent = {};
  export const Strike = {};
  export const StrikeContent = {};
  export const ActionRow = {};
  export const FormRow = {};
  export const A = {color:"#4286f4"};
  export const Hint = {};
  export const Radio = {};
  export const InputLabel = {};
  export const AmazonSignInButton = {};
  export const FacebookSignInButton = {};
  export const GoogleSignInButton = {};
  export const OAuthSignInButton = {};
  export const Toast = {};
  // export const NavBar = {};
  // export const NavRight = {};
  // export const Nav = {};
  // export const NavItem = {};
  // export const NavButton = {};
  
  const AmplifyTheme = {
    container: Container,
    formContainer: FormContainer,
    formSection: FormSection,
    formField: FormField,
  
    sectionHeader: SectionHeader,
    sectionBody: SectionBody,
    sectionFooter: SectionFooter,
    sectionFooterPrimaryContent: SectionFooterPrimaryContent,
    sectionFooterSecondaryContent: SectionFooterSecondaryContent,
  
    input: Input,
    button: Button,
    photoPickerButton: PhotoPickerButton,
    photoPlaceholder: PhotoPlaceholder,
    signInButton: SignInButton,
    signInButtonIcon: SignInButtonIcon,
    signInButtonContent: SignInButtonContent,
    amazonSignInButton: AmazonSignInButton,
    facebookSignInButton: FacebookSignInButton,
    googleSignInButton: GoogleSignInButton,
    oAuthSignInButton: OAuthSignInButton,
  
    formRow: FormRow,
    strike: Strike,
    strikeContent: StrikeContent,
    actionRow: ActionRow,
    a: A,
  
    hint: Hint,
    radio: Radio,
    inputLabel: InputLabel,
    toast: Toast,

  };
  
  export default AmplifyTheme;